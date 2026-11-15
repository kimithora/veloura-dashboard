from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from core.mixins import RoleRequiredMixin
from .models import Material, StockMovement
from .forms import MaterialForm, StockAdjustmentForm


class MaterialListView(RoleRequiredMixin, ListView):
    required_roles = ('ADMIN', 'CASHIER')
    template_name = 'catalog/list.html'
    context_object_name = 'materials'
    paginate_by = 20

    def get_queryset(self):
        qs = Material.objects.select_related('supplier').all()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx.update({
            'title': 'Materials',
            'subtitle': 'Raw and supporting materials inventory',
            'icon': 'package',
            'object_list': qs,
            'columns': [
                {'header': 'Material ID', 'field': 'material_id'},
                {'header': 'Name', 'field': 'name'},
                {'header': 'Category', 'field': 'get_category_display'},
                {'header': 'Unit', 'field': 'get_unit_display'},
                {'header': 'Stock', 'field': 'stock_quantity'},
                {'header': 'Min Stock', 'field': 'min_stock'},
                {'header': 'Status', 'field': None},
            ],
            'create_url': 'inventory:material_add',
            'create_label': 'Add Material',
            'edit_url': 'inventory:material_edit',
            'empty_message': 'No materials found.',
            'query': self.request.GET.get('q', ''),
        })
        return ctx


class MaterialCreateView(RoleRequiredMixin, CreateView):
    required_roles = ('ADMIN', 'CASHIER')
    model = Material
    form_class = MaterialForm
    template_name = 'catalog/form.html'
    success_url = reverse_lazy('inventory:material_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Add Material',
            'subtitle': 'Register a new material',
            'icon': 'package',
            'cancel_url': reverse_lazy('inventory:material_list'),
        })
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Material created successfully.')
        return super().form_valid(form)


class MaterialUpdateView(RoleRequiredMixin, UpdateView):
    required_roles = ('ADMIN', 'CASHIER')
    model = Material
    form_class = MaterialForm
    template_name = 'catalog/form.html'
    success_url = reverse_lazy('inventory:material_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Edit Material',
            'subtitle': 'Update material details',
            'icon': 'edit-2',
            'cancel_url': reverse_lazy('inventory:material_list'),
        })
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Material updated successfully.')
        return super().form_valid(form)


class MaterialDeleteView(RoleRequiredMixin, DeleteView):
    required_roles = ('ADMIN',)
    model = Material
    template_name = 'catalog/confirm_delete.html'
    success_url = reverse_lazy('inventory:material_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Delete Material',
            'subtitle': 'Remove this material',
            'object_name': 'Material',
            'object': self.object.name,
            'cancel_url': reverse_lazy('inventory:material_list'),
        })
        return ctx


class StockMovementListView(RoleRequiredMixin, ListView):
    required_roles = ('ADMIN', 'CASHIER')
    template_name = 'catalog/list.html'
    context_object_name = 'movements'
    paginate_by = 30

    def get_queryset(self):
        return StockMovement.objects.select_related('user').all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx.update({
            'title': 'Stock Movement Ledger',
            'subtitle': 'Every inventory change is recorded here',
            'icon': 'activity',
            'object_list': qs,
            'columns': [
                {'header': 'Date', 'field': 'created_at'},
                {'header': 'Type', 'field': 'get_movement_type_display'},
                {'header': 'Item', 'field': 'item'},
                {'header': 'Quantity', 'field': 'quantity'},
                {'header': 'Previous Stock', 'field': 'previous_stock'},
                {'header': 'New Stock', 'field': 'new_stock'},
                {'header': 'User', 'field': 'user.username'},
                {'header': 'Reference', 'field': 'reference'},
            ],
            'create_url': None,
            'empty_message': 'No stock movements recorded.',
            'query': self.request.GET.get('q', ''),
        })
        return ctx


@login_required
def material_stock_adjust(request, pk):
    """Adjust stock for a material (purchase, return, adjustment, damage/loss)."""
    material = get_object_or_404(Material, pk=pk)
    if not request.user.has_role('ADMIN') and not request.user.has_role('CASHIER'):
        messages.error(request, 'You are not authorized to adjust inventory.')
        return redirect('inventory:material_list')

    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            movement_type = form.cleaned_data['movement_type']
            quantity = form.cleaned_data['quantity']
            reference = form.cleaned_data.get('reference') or ''
            notes = form.cleaned_data.get('notes') or ''

            previous_stock = material.stock_quantity
            if movement_type == StockMovement.MovementType.DAMAGE_LOSS:
                new_stock = previous_stock - quantity
                if new_stock < 0:
                    messages.error(request, 'Insufficient stock for damage/loss removal.')
                    return redirect('inventory:material_stock_adjust', pk=material.pk)
            else:
                new_stock = previous_stock + quantity

            with transaction.atomic():
                movement = StockMovement.objects.create(
                    content_type=ContentType.objects.get_for_model(Material),
                    object_id=material.pk,
                    movement_type=movement_type,
                    quantity=quantity,
                    previous_stock=previous_stock,
                    new_stock=new_stock,
                    reference=reference,
                    user=request.user,
                    notes=notes,
                )
                material.stock_quantity = new_stock
                material.save(update_fields=['stock_quantity', 'updated_at'])
            messages.success(
                request,
                'Stock adjusted: {} {} -> new stock {}'.format(movement_type, quantity, new_stock)
            )
            return redirect('inventory:material_list')
    else:
        form = StockAdjustmentForm()

    return render(request, 'catalog/form.html', {
        'title': 'Adjust Stock',
        'subtitle': 'Adjust stock for {}'.format(material.name),
        'icon': 'activity',
        'form': form,
        'cancel_url': reverse_lazy('inventory:material_list'),
    })
