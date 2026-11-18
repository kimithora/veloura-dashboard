from django import forms
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction as db_transaction
from django.db.models import Q

from core.mixins import RoleRequiredMixin
from .models import Design, DesignVersion
from .forms import DesignForm
from orders.models import Order


class DesignListView(RoleRequiredMixin, ListView):
    required_roles = ('ADMIN', 'DESIGNER', 'CASHIER')
    template_name = 'catalog/list.html'
    context_object_name = 'designs'
    paginate_by = 20

    def get_queryset(self):
        qs = Design.objects.select_related('order', 'designer').all()
        if self.request.user.has_role('DESIGNER'):
            # Designer sees own designs and unassigned designs (available to claim).
            qs = qs.filter(Q(designer=self.request.user) | Q(designer__isnull=True))
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(design_id__icontains=q) |
                Q(name__icontains=q) |
                Q(order__order_number__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        create_url = 'designs:design_add' if not self.request.user.has_role('DESIGNER') else None
        create_label = 'Add Design' if create_url else None
        ctx.update({
            'title': 'Designs',
            'subtitle': 'Manage fashion designs',
            'icon': 'layout',
            'object_list': qs,
            'columns': [
                {'header': 'Design ID', 'field': 'design_id', 'detail_url': 'designs:design_detail'},
                {'header': 'Name', 'field': 'name'},
                {'header': 'Order', 'field': 'order.order_number'},
                {'header': 'Category', 'field': 'get_category_display'},
                {'header': 'Status', 'field': 'get_status_display'},
                {'header': 'Designer', 'field': 'designer.username'},
            ],
            'create_url': create_url,
            'create_label': create_label,
            'detail_url': 'designs:design_detail',
            'edit_url': 'designs:design_edit',
            'empty_message': 'No designs found.',
            'query': self.request.GET.get('q', ''),
        })
        return ctx


class DesignCreateView(RoleRequiredMixin, CreateView):
    required_roles = ('ADMIN', 'DESIGNER')
    model = Design
    form_class = DesignForm
    template_name = 'catalog/form.html'

    def dispatch(self, request, *args, **kwargs):
        order_pk = request.GET.get('order')
        self.preselect_order = None
        if order_pk:
            self.preselect_order = get_object_or_404(Order, pk=order_pk)
            # Designer cannot create a design for another designer's order.
            if request.user.has_role('DESIGNER'):
                if self.preselect_order.designer_id not in (None, request.user.pk):
                    return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.preselect_order:
            return reverse('orders:order_detail', kwargs={'pk': self.preselect_order.pk})
        return reverse_lazy('designs:design_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Add Design',
            'subtitle': 'Create a new fashion design',
            'icon': 'layout',
            'cancel_url': self.get_success_url(),
            'preselect_order': self.preselect_order,
        })
        return ctx

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.has_role('DESIGNER'):
            # Designer creating a design is automatically its designer.
            form.fields['designer'].initial = self.request.user
            form.fields['designer'].widget = forms.HiddenInput()
            # Designer may only pick own or unassigned orders.
            form.fields['order'].queryset = Order.objects.filter(
                Q(designer=self.request.user) | Q(designer__isnull=True)
            )
        if self.preselect_order:
            form.fields['order'].initial = self.preselect_order
            form.fields['order'].widget = forms.HiddenInput()
            if not form.initial.get('name'):
                form.fields['name'].initial = 'Design - {}'.format(
                    self.preselect_order.order_number)
        return form

    def form_valid(self, form):
        if self.request.user.has_role('DESIGNER'):
            form.instance.designer = self.request.user
        if self.preselect_order:
            form.instance.order = self.preselect_order
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Design created successfully.')
        return super().form_valid(form)


class DesignUpdateView(RoleRequiredMixin, UpdateView):
    required_roles = ('ADMIN', 'DESIGNER')
    model = Design
    form_class = DesignForm
    template_name = 'catalog/form.html'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_role('DESIGNER'):
            # Designer can edit own designs and claim unassigned ones.
            qs = qs.filter(Q(designer=self.request.user) | Q(designer__isnull=True))
        return qs

    def get_success_url(self):
        return reverse('designs:design_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Edit Design',
            'subtitle': 'Update design details',
            'icon': 'edit-2',
            'cancel_url': reverse('designs:design_detail', kwargs={'pk': self.object.pk}),
        })
        return ctx

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.has_role('DESIGNER'):
            # Designer editing may only move the design between own/unassigned orders.
            form.fields['order'].queryset = Order.objects.filter(
                Q(designer=self.request.user) | Q(designer__isnull=True)
            )
        return form

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Design updated successfully.')
        return super().form_valid(form)


class DesignDetailView(RoleRequiredMixin, DetailView):
    required_roles = ('ADMIN', 'DESIGNER', 'CASHIER')
    model = Design
    template_name = 'designs/design_detail.html'
    context_object_name = 'design'

    def get_queryset(self):
        qs = Design.objects.select_related('order', 'designer').all()
        if self.request.user.has_role('DESIGNER'):
            qs = qs.filter(Q(designer=self.request.user) | Q(designer__isnull=True))
        return qs


@login_required
@require_POST
def update_design_status(request, pk):
    design = get_object_or_404(Design, pk=pk)
    if not request.user.has_role('ADMIN') and not request.user.has_role('DESIGNER'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    # Designer can only update designs assigned to them.
    if request.user.has_role('DESIGNER'):
        if design.designer_id is None:
            # Claim the design by updating its status.
            design.designer = request.user
            design.save(update_fields=['designer', 'updated_at'])
        elif design.designer_id != request.user.pk:
            return JsonResponse({'error': 'You can only update designs assigned to you.'}, status=403)
    new_status = request.POST.get('status')
    notes = request.POST.get('notes', '')
    if new_status not in dict(Design.Status.choices):
        return JsonResponse({'error': 'Invalid status'}, status=400)
    with db_transaction.atomic():
        design.status = new_status
        design.updated_by = request.user
        design.save(update_fields=['status', 'updated_at', 'updated_by'])
        # Auto-update order status when design is approved
        if new_status == Design.Status.APPROVED:
            order = design.order
            if order.status in ('RECEIVED', 'MEASUREMENT', 'DESIGNING'):
                order.status = Order.Status.DESIGN_APPROVAL
                order.updated_by = request.user
                order.save(update_fields=['status', 'updated_at', 'updated_by'])
                from orders.models import OrderStatusHistory
                OrderStatusHistory.objects.create(
                    order=order, status=order.status, changed_by=request.user,
                    notes='Design {} approved'.format(design.design_id),
                )
        # Create a version snapshot with an incremented version number to
        # avoid IntegrityError on unique_together (design, version_number).
        last_version = DesignVersion.objects.filter(design=design).order_by('-version_number').first()
        next_version = (last_version.version_number + 1) if last_version else (design.version or 1)
        DesignVersion.objects.create(
            design=design, version_number=next_version,
            sketch=design.sketch, notes=notes or 'Version snapshot',
            created_by=request.user,
        )
        # Keep design.version in sync with the latest snapshot.
        if not design.version or design.version < next_version:
            design.version = next_version
            design.save(update_fields=['version', 'updated_at'])
    messages.success(request, 'Design status updated to {}.'.format(design.get_status_display()))
    return JsonResponse({'ok': True, 'new_status': design.get_status_display()})
