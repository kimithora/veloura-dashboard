from django import forms
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction as db_transaction
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from core.mixins import RoleRequiredMixin
from .models import Production, MaterialRequest, MaterialUsage, Fitting, QualityControl
from .forms import ProductionForm, MaterialRequestForm, MaterialRequestActionForm, QualityControlForm
from orders.models import Order
from inventory.models import Material, StockMovement


class ProductionListView(RoleRequiredMixin, ListView):
    required_roles = ('ADMIN', 'DESIGNER')
    template_name = 'catalog/list.html'
    context_object_name = 'productions'
    paginate_by = 20

    def get_queryset(self):
        qs = Production.objects.select_related('order', 'designer').all()
        if self.request.user.has_role('DESIGNER'):
            # Designer sees own productions and unassigned ones (claimable).
            qs = qs.filter(Q(designer=self.request.user) | Q(designer__isnull=True))
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(production_id__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        create_url = 'production:production_add' if not self.request.user.has_role('DESIGNER') else None
        create_label = 'Add Production' if create_url else None
        ctx.update({
            'title': 'Production',
            'subtitle': 'Manage production orders',
            'icon': 'layers',
            'object_list': qs,
            'columns': [
                {'header': 'Production ID', 'field': 'production_id', 'detail_url': 'production:production_detail'},
                {'header': 'Order', 'field': 'order.order_number'},
                {'header': 'Designer', 'field': 'designer.username'},
                {'header': 'Status', 'field': 'get_status_display'},
                {'header': 'Progress', 'field': 'progress'},
                {'header': 'Est. Completion', 'field': 'estimated_completion'},
            ],
            'create_url': create_url,
            'create_label': create_label,
            'detail_url': 'production:production_detail',
            'empty_message': 'No production records found.',
            'query': self.request.GET.get('q', ''),
        })
        return ctx


class ProductionCreateView(RoleRequiredMixin, CreateView):
    required_roles = ('ADMIN', 'DESIGNER')
    model = Production
    form_class = ProductionForm
    template_name = 'catalog/form.html'

    def dispatch(self, request, *args, **kwargs):
        order_pk = request.GET.get('order')
        self.preselect_order = None
        if order_pk:
            self.preselect_order = get_object_or_404(Order, pk=order_pk)
            if request.user.has_role('DESIGNER'):
                if self.preselect_order.designer_id not in (None, request.user.pk):
                    return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.preselect_order:
            return reverse('orders:order_detail', kwargs={'pk': self.preselect_order.pk})
        return reverse_lazy('production:production_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Add Production',
            'subtitle': 'Create a new production record',
            'icon': 'layers',
            'cancel_url': self.get_success_url(),
            'preselect_order': self.preselect_order,
        })
        return ctx

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.has_role('DESIGNER'):
            # Designer creating a production is automatically its designer.
            form.fields['designer'].initial = self.request.user
            form.fields['designer'].widget = forms.HiddenInput()
            # Designer may only pick own or unassigned orders.
            form.fields['order'].queryset = Order.objects.filter(
                Q(designer=self.request.user) | Q(designer__isnull=True)
            )
        if self.preselect_order:
            form.fields['order'].initial = self.preselect_order
            form.fields['order'].widget = forms.HiddenInput()
        return form

    def form_valid(self, form):
        if self.request.user.has_role('DESIGNER'):
            form.instance.designer = self.request.user
        if self.preselect_order:
            form.instance.order = self.preselect_order
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Production created successfully.')
        return super().form_valid(form)


class ProductionDetailView(RoleRequiredMixin, DetailView):
    required_roles = ('ADMIN', 'DESIGNER')
    model = Production
    template_name = 'production/production_detail.html'
    context_object_name = 'production'

    def get_queryset(self):
        qs = Production.objects.select_related('order', 'designer').all()
        if self.request.user.has_role('DESIGNER'):
            # Designer sees own productions and unassigned ones (claimable).
            qs = qs.filter(Q(designer=self.request.user) | Q(designer__isnull=True))
        return qs


@login_required
@require_POST
def production_update(request, pk):
    """Update production progress and status."""
    production = get_object_or_404(Production, pk=pk)
    if not request.user.has_role('ADMIN') and not request.user.has_role('DESIGNER'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    # Designer can only update productions assigned to them, or claim an unassigned one.
    if request.user.has_role('DESIGNER'):
        if production.designer_id is None:
            # Claim the production by updating its progress.
            production.designer = request.user
            production.updated_by = request.user
            production.save(update_fields=['designer', 'updated_at', 'updated_by'])
        elif production.designer_id != request.user.pk:
            return JsonResponse({'error': 'You can only update productions assigned to you.'}, status=403)
    progress = request.POST.get('progress')
    status = request.POST.get('status')
    notes = request.POST.get('notes', '')
    try:
        progress = int(progress)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid progress'}, status=400)
    if progress < 0 or progress > 100:
        return JsonResponse({'error': 'Progress must be 0-100'}, status=400)
    if status not in dict(Production.Status.choices):
        return JsonResponse({'error': 'Invalid status'}, status=400)
    with db_transaction.atomic():
        production.progress = progress
        production.status = status
        if status == Production.Status.COMPLETED and not production.actual_completion:
            production.actual_completion = timezone.localdate()
        production.updated_by = request.user
        production.save(update_fields=['progress', 'status', 'actual_completion', 'updated_at', 'updated_by'])
        if notes:
            production.notes = (production.notes or '') + '\n' + notes
            production.updated_by = request.user
            production.save(update_fields=['notes', 'updated_at', 'updated_by'])
    messages.success(request, 'Production progress updated.')
    return JsonResponse({'ok': True})


class MaterialRequestListView(RoleRequiredMixin, ListView):
    required_roles = ('ADMIN', 'DESIGNER')
    template_name = 'catalog/list.html'
    context_object_name = 'requests'
    paginate_by = 20

    def get_queryset(self):
        qs = MaterialRequest.objects.select_related('production', 'material', 'requested_by').all()
        if self.request.user.has_role('DESIGNER'):
            qs = qs.filter(production__designer=self.request.user)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(request_id__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        create_url = 'production:material_request_add' if not self.request.user.has_role('DESIGNER') else None
        create_label = 'Request Material' if create_url else None
        ctx.update({
            'title': 'Material Requests',
            'subtitle': 'Request raw/supporting materials from inventory',
            'icon': 'package',
            'object_list': qs,
            'columns': [
                {'header': 'Request ID', 'field': 'request_id'},
                {'header': 'Production', 'field': 'production.production_id'},
                {'header': 'Material', 'field': 'material.name'},
                {'header': 'Quantity', 'field': 'quantity'},
                {'header': 'Status', 'field': 'get_status_display'},
                {'header': 'Requested By', 'field': 'requested_by.username'},
            ],
            'create_url': create_url,
            'create_label': create_label,
            'empty_message': 'No material requests found.',
            'query': self.request.GET.get('q', ''),
        })
        return ctx


class MaterialRequestCreateView(RoleRequiredMixin, CreateView):
    required_roles = ('ADMIN', 'DESIGNER')
    model = MaterialRequest
    form_class = MaterialRequestForm
    template_name = 'catalog/form.html'

    def dispatch(self, request, *args, **kwargs):
        production_pk = request.GET.get('production')
        self.preselect_production = None
        if production_pk:
            self.preselect_production = get_object_or_404(Production, pk=production_pk)
            if request.user.has_role('DESIGNER') and self.preselect_production.designer_id != request.user.pk:
                return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.preselect_production:
            return reverse('production:production_detail', kwargs={'pk': self.preselect_production.pk})
        return reverse_lazy('production:material_request_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Request Material',
            'subtitle': 'Request materials for production',
            'icon': 'package',
            'cancel_url': self.get_success_url(),
            'preselect_production': self.preselect_production,
        })
        return ctx

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.has_role('DESIGNER'):
            form.fields['production'].queryset = Production.objects.filter(designer=self.request.user)
        if self.preselect_production:
            form.fields['production'].initial = self.preselect_production
            form.fields['production'].widget = forms.HiddenInput()
        return form

    def form_valid(self, form):
        form.instance.requested_by = self.request.user
        if self.preselect_production:
            form.instance.production = self.preselect_production
        # Defense in depth: designer may only request materials for own productions.
        if self.request.user.has_role('DESIGNER') and form.instance.production.designer_id != self.request.user.pk:
            messages.error(self.request, 'You can only request materials for your own productions.')
            return self.form_invalid(form)
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Material request created.')
        return super().form_valid(form)


@login_required
@require_POST
def material_request_action(request, pk):
    req = get_object_or_404(MaterialRequest, pk=pk)
    if not request.user.has_role('ADMIN') and not request.user.has_role('DESIGNER'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    # Designer can only act on material requests for their own productions.
    if request.user.has_role('DESIGNER') and req.production.designer_id != request.user.pk:
        return JsonResponse({'error': 'You can only act on requests for your own productions.'}, status=403)
    form = MaterialRequestActionForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'Invalid action'}, status=400)
    action = form.cleaned_data['action']
    with db_transaction.atomic():
        if action == 'approve':
            req.status = MaterialRequest.Status.APPROVED
            req.approved_by = request.user
            req.updated_by = request.user
            req.save(update_fields=['status', 'approved_by', 'updated_at', 'updated_by'])
            messages.success(request, 'Material request approved.')
        elif action == 'fulfill':
            # Kurangi stok material dan catat ledger saat permintaan terpenuhi.
            material = req.material
            with db_transaction.atomic():
                material = Material.objects.select_for_update().get(pk=material.pk)
                previous_stock = material.stock_quantity
                new_stock = previous_stock - req.quantity
                if new_stock < 0:
                    return JsonResponse({
                        'error': 'Insufficient material stock for {}: have {}, need {}'.format(
                            material.name, previous_stock, req.quantity
                        )
                    }, status=400)
                material.stock_quantity = new_stock
                material.updated_by = request.user
                material.save(update_fields=['stock_quantity', 'updated_at', 'updated_by'])
                StockMovement.objects.create(
                    content_type=ContentType.objects.get_for_model(Material),
                    object_id=material.pk,
                    movement_type=StockMovement.MovementType.PRODUCTION_USAGE,
                    quantity=req.quantity,
                    previous_stock=previous_stock,
                    new_stock=new_stock,
                    reference=req.request_id,
                    user=request.user,
                    notes='Material request fulfilled: {}'.format(req.request_id),
                )
            req.status = MaterialRequest.Status.FULFILLED
            req.approved_by = request.user
            req.updated_by = request.user
            req.save(update_fields=['status', 'approved_by', 'updated_at', 'updated_by'])
            messages.success(request, 'Material request fulfilled. Stok dikurangi dan dicatat di ledger.')
        elif action == 'reject':
            req.status = MaterialRequest.Status.REJECTED
            req.approved_by = request.user
            req.updated_by = request.user
            req.save(update_fields=['status', 'approved_by', 'updated_at', 'updated_by'])
            messages.success(request, 'Material request rejected.')
    return JsonResponse({'ok': True, 'new_status': req.get_status_display()})


class MaterialUsageCreateView(RoleRequiredMixin, CreateView):
    required_roles = ('ADMIN', 'DESIGNER')
    model = MaterialUsage
    fields = ['production', 'material_request', 'material', 'quantity_used', 'notes']
    template_name = 'catalog/form.html'

    def dispatch(self, request, *args, **kwargs):
        production_pk = request.GET.get('production')
        self.preselect_production = None
        if production_pk:
            self.preselect_production = get_object_or_404(Production, pk=production_pk)
            if request.user.has_role('DESIGNER') and self.preselect_production.designer_id not in (None, request.user.pk):
                return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.preselect_production:
            return reverse('production:production_detail', kwargs={'pk': self.preselect_production.pk})
        return reverse_lazy('production:production_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Record Material Usage',
            'subtitle': 'Record materials consumed in production',
            'icon': 'activity',
            'cancel_url': self.get_success_url(),
            'preselect_production': self.preselect_production,
        })
        return ctx

    def form_valid(self, form):
        form.instance.used_by = self.request.user
        if self.preselect_production:
            form.instance.production = self.preselect_production
        # Defense in depth: designer may only record usage for own/claimable productions.
        if self.request.user.has_role('DESIGNER'):
            if form.instance.production.designer_id is None:
                # Claim the production by recording material usage on it.
                form.instance.production.designer = self.request.user
                form.instance.production.updated_by = self.request.user
                form.instance.production.save(update_fields=['designer', 'updated_at', 'updated_by'])
            elif form.instance.production.designer_id != self.request.user.pk:
                messages.error(self.request, 'You can only record material usage for your own productions.')
                return self.form_invalid(form)
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        with db_transaction.atomic():
            usage = form.save(commit=False)
            # Lock material row to prevent concurrent stock updates (race condition).
            material = Material.objects.select_for_update().get(pk=usage.material.pk)
            previous_stock = material.stock_quantity
            new_stock = previous_stock - usage.quantity_used
            if new_stock < 0:
                messages.error(self.request, 'Insufficient material stock.')
                return self.form_invalid(form)
            material.stock_quantity = new_stock
            material.updated_by = self.request.user
            material.save(update_fields=['stock_quantity', 'updated_at', 'updated_by'])
            usage.save()
            StockMovement.objects.create(
                content_type=ContentType.objects.get_for_model(Material),
                object_id=material.pk,
                movement_type=StockMovement.MovementType.PRODUCTION_USAGE,
                quantity=usage.quantity_used,
                previous_stock=previous_stock,
                new_stock=new_stock,
                reference=usage.production.production_id,
                user=self.request.user,
                notes='Material usage for production {}'.format(usage.production.production_id),
            )
        messages.success(self.request, 'Material usage recorded. Inventory updated.')
        return redirect(self.get_success_url())

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.has_role('DESIGNER'):
            # Designer only sees own productions and claimable unassigned ones.
            form.fields['production'].queryset = Production.objects.filter(
                Q(designer=self.request.user) | Q(designer__isnull=True)
            )
            form.fields['material_request'].queryset = MaterialRequest.objects.filter(
                Q(production__designer=self.request.user) | Q(production__designer__isnull=True)
            )
        if self.preselect_production:
            form.fields['production'].initial = self.preselect_production
            form.fields['production'].widget = forms.HiddenInput()
        for name in ('production', 'material_request', 'material'):
            form.fields[name].widget.attrs['class'] = 'form-select'
        form.fields['quantity_used'].widget.attrs.update({'class': 'form-control', 'step': '0.001'})
        form.fields['notes'].widget.attrs.update({'class': 'form-control', 'rows': 3})
        return form


class QualityControlListView(RoleRequiredMixin, ListView):
    required_roles = ('ADMIN', 'DESIGNER')
    template_name = 'catalog/list.html'
    context_object_name = 'qcs'
    paginate_by = 20

    def get_queryset(self):
        qs = QualityControl.objects.select_related('order', 'qc_by').all()
        if self.request.user.has_role('DESIGNER'):
            # Designer sees QC for own orders and unassigned (claimable) orders.
            qs = qs.filter(Q(order__designer=self.request.user) | Q(order__designer__isnull=True))
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(qc_id__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        create_url = 'production:qc_add' if not self.request.user.has_role('DESIGNER') else None
        create_label = 'Add QC Check' if create_url else None
        ctx.update({
            'title': 'Quality Control',
            'subtitle': 'Quality control checklist for orders',
            'icon': 'check-circle-2',
            'object_list': qs,
            'columns': [
                {'header': 'QC ID', 'field': 'qc_id'},
                {'header': 'Order', 'field': 'order.order_number'},
                {'header': 'Status', 'field': 'get_status_display'},
                {'header': 'QC By', 'field': 'qc_by.username'},
                {'header': 'Date', 'field': 'qc_date'},
            ],
            'create_url': create_url,
            'create_label': create_label,
            'empty_message': 'No QC records found.',
            'query': self.request.GET.get('q', ''),
        })
        return ctx


class QualityControlCreateView(RoleRequiredMixin, CreateView):
    required_roles = ('ADMIN', 'DESIGNER')
    model = QualityControl
    form_class = QualityControlForm
    template_name = 'catalog/form.html'

    def dispatch(self, request, *args, **kwargs):
        order_pk = request.GET.get('order')
        self.preselect_order = None
        if order_pk:
            self.preselect_order = get_object_or_404(Order, pk=order_pk)
            if request.user.has_role('DESIGNER'):
                if self.preselect_order.designer_id not in (None, request.user.pk):
                    return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.preselect_order:
            return reverse('orders:order_detail', kwargs={'pk': self.preselect_order.pk})
        return reverse_lazy('production:qc_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Quality Control',
            'subtitle': 'Perform quality control check',
            'icon': 'check-circle-2',
            'cancel_url': self.get_success_url(),
            'preselect_order': self.preselect_order,
        })
        return ctx

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.has_role('DESIGNER'):
            # Designer performing QC is always the QC performer.
            form.fields['qc_by'].initial = self.request.user
            form.fields['qc_by'].widget = forms.HiddenInput()
            # Designer may only pick own or unassigned orders.
            form.fields['order'].queryset = Order.objects.filter(
                Q(designer=self.request.user) | Q(designer__isnull=True)
            )
        if self.preselect_order:
            form.fields['order'].initial = self.preselect_order
            form.fields['order'].widget = forms.HiddenInput()
        return form

    def form_valid(self, form):
        if self.preselect_order:
            form.instance.order = self.preselect_order
        form.instance.qc_by = self.request.user
        if form.instance.status == QualityControl.Status.PASSED:
            if not form.instance.all_checks_passed:
                messages.error(self.request, 'QC cannot be PASSED until all checklist items are checked.')
                return self.form_invalid(form)
            form.instance.qc_date = timezone.now()
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'QC check recorded.')
        return super().form_valid(form)


class FittingListView(RoleRequiredMixin, ListView):
    required_roles = ('ADMIN', 'DESIGNER')
    model = Fitting
    template_name = 'catalog/list.html'
    context_object_name = 'fittings'
    paginate_by = 20

    def get_queryset(self):
        qs = Fitting.objects.select_related('order', 'customer').all()
        if self.request.user.has_role('DESIGNER'):
            # Designer sees fittings for own orders and unassigned (claimable) orders.
            qs = qs.filter(Q(order__designer=self.request.user) | Q(order__designer__isnull=True))
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(fitting_id__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        create_url = 'production:fitting_add' if not self.request.user.has_role('DESIGNER') else None
        create_label = 'Add Fitting' if create_url else None
        ctx.update({
            'title': 'Fittings',
            'subtitle': 'Fitting sessions for custom orders',
            'icon': 'calendar',
            'object_list': qs,
            'columns': [
                {'header': 'Fitting ID', 'field': 'fitting_id'},
                {'header': 'Order', 'field': 'order.order_number'},
                {'header': 'Customer', 'field': 'customer.full_name'},
                {'header': 'Scheduled', 'field': 'scheduled_date'},
                {'header': 'Status', 'field': 'get_status_display'},
            ],
            'create_url': create_url,
            'create_label': create_label,
            'empty_message': 'No fitting records found.',
            'query': self.request.GET.get('q', ''),
        })
        return ctx


class FittingCreateView(RoleRequiredMixin, CreateView):
    required_roles = ('ADMIN', 'DESIGNER')
    model = Fitting
    fields = ['order', 'customer', 'scheduled_date', 'fitting_date', 'results', 'alterations_required', 'documentation', 'status']
    template_name = 'catalog/form.html'

    def dispatch(self, request, *args, **kwargs):
        order_pk = request.GET.get('order')
        self.preselect_order = None
        if order_pk:
            self.preselect_order = get_object_or_404(Order, pk=order_pk)
            if request.user.has_role('DESIGNER'):
                if self.preselect_order.designer_id not in (None, request.user.pk):
                    return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.preselect_order:
            return reverse('orders:order_detail', kwargs={'pk': self.preselect_order.pk})
        return reverse_lazy('production:fitting_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Add Fitting',
            'subtitle': 'Schedule a fitting session',
            'icon': 'calendar',
            'cancel_url': self.get_success_url(),
            'preselect_order': self.preselect_order,
        })
        return ctx

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.has_role('DESIGNER'):
            # Designer may only pick own or unassigned orders.
            form.fields['order'].queryset = Order.objects.filter(
                Q(designer=self.request.user) | Q(designer__isnull=True)
            )
        if self.preselect_order:
            form.fields['order'].initial = self.preselect_order
            form.fields['order'].widget = forms.HiddenInput()
            form.fields['customer'].initial = self.preselect_order.customer
            form.fields['customer'].widget = forms.HiddenInput()
        for name in ('order', 'customer', 'status'):
            if name in form.fields:
                form.fields[name].widget.attrs['class'] = 'form-select'
        form.fields['scheduled_date'].widget.attrs.update({'class': 'form-control', 'type': 'datetime-local'})
        form.fields['fitting_date'].widget.attrs.update({'class': 'form-control', 'type': 'datetime-local'})
        form.fields['results'].widget.attrs.update({'class': 'form-control', 'rows': 3})
        form.fields['alterations_required'].widget.attrs.update({'class': 'form-control', 'rows': 3})
        return form

    def form_valid(self, form):
        if self.preselect_order:
            form.instance.order = self.preselect_order
            form.instance.customer = self.preselect_order.customer
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Fitting scheduled successfully.')
        return super().form_valid(form)
