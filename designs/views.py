from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction as db_transaction

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
            qs = qs.filter(designer=self.request.user)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(design_id__icontains=q) | qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx.update({
            'title': 'Designs',
            'subtitle': 'Manage fashion designs',
            'icon': 'layout',
            'object_list': qs,
            'columns': [
                {'header': 'Design ID', 'field': 'design_id'},
                {'header': 'Name', 'field': 'name'},
                {'header': 'Order', 'field': 'order.order_number'},
                {'header': 'Category', 'field': 'get_category_display'},
                {'header': 'Status', 'field': 'get_status_display'},
                {'header': 'Designer', 'field': 'designer.username'},
            ],
            'create_url': 'designs:design_add',
            'create_label': 'Add Design',
            'detail_url': 'designs:design_detail',
            'empty_message': 'No designs found.',
            'query': self.request.GET.get('q', ''),
        })
        return ctx


class DesignCreateView(RoleRequiredMixin, CreateView):
    required_roles = ('ADMIN', 'DESIGNER')
    model = Design
    form_class = DesignForm
    template_name = 'catalog/form.html'
    success_url = reverse_lazy('designs:design_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Add Design',
            'subtitle': 'Create a new fashion design',
            'icon': 'layout',
            'cancel_url': reverse_lazy('designs:design_list'),
        })
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Design created successfully.')
        return super().form_valid(form)


class DesignUpdateView(RoleRequiredMixin, UpdateView):
    required_roles = ('ADMIN', 'DESIGNER')
    model = Design
    form_class = DesignForm
    template_name = 'catalog/form.html'
    success_url = reverse_lazy('designs:design_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Edit Design',
            'subtitle': 'Update design details',
            'icon': 'edit-2',
            'cancel_url': reverse_lazy('designs:design_list'),
        })
        return ctx


class DesignDetailView(RoleRequiredMixin, DetailView):
    required_roles = ('ADMIN', 'DESIGNER', 'CASHIER')
    model = Design
    template_name = 'designs/design_detail.html'
    context_object_name = 'design'

    def get_queryset(self):
        qs = Design.objects.select_related('order', 'designer').all()
        if self.request.user.has_role('DESIGNER'):
            qs = qs.filter(designer=self.request.user)
        return qs


@login_required
@require_POST
def update_design_status(request, pk):
    design = get_object_or_404(Design, pk=pk)
    if not request.user.has_role('ADMIN') and not request.user.has_role('DESIGNER'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    new_status = request.POST.get('status')
    notes = request.POST.get('notes', '')
    if new_status not in dict(Design.Status.choices):
        return JsonResponse({'error': 'Invalid status'}, status=400)
    with db_transaction.atomic():
        design.status = new_status
        design.save(update_fields=['status', 'updated_at'])
        # Auto-update order status when design is approved
        if new_status == Design.Status.APPROVED:
            order = design.order
            if order.status in ('RECEIVED', 'MEASUREMENT', 'DESIGNING'):
                order.status = Order.Status.DESIGN_APPROVAL
                order.save(update_fields=['status', 'updated_at'])
                from orders.models import OrderStatusHistory
                OrderStatusHistory.objects.create(
                    order=order, status=order.status, changed_by=request.user,
                    notes='Design {} approved'.format(design.design_id),
                )
        # Create a version snapshot
        DesignVersion.objects.create(
            design=design, version_number=design.version,
            sketch=design.sketch, notes=notes or 'Version snapshot',
            created_by=request.user,
        )
    messages.success(request, 'Design status updated to {}.'.format(design.get_status_display()))
    return JsonResponse({'ok': True, 'new_status': design.get_status_display()})
