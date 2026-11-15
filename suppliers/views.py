from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from core.mixins import RoleRequiredMixin
from .models import Supplier
from .forms import SupplierForm


class SupplierListView(RoleRequiredMixin, ListView):
    required_roles = ('ADMIN', 'CASHIER')
    template_name = 'catalog/list.html'
    context_object_name = 'suppliers'
    paginate_by = 20

    def get_queryset(self):
        qs = Supplier.objects.all()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx.update({
            'title': 'Suppliers',
            'subtitle': 'Manage suppliers (direct purchase & consignment)',
            'icon': 'truck',
            'object_list': qs,
            'columns': [
                {'header': 'Supplier ID', 'field': 'supplier_id'},
                {'header': 'Name', 'field': 'name'},
                {'header': 'Contact Person', 'field': 'contact_person'},
                {'header': 'Type', 'field': 'get_supplier_type_display'},
                {'header': 'Phone', 'field': 'phone'},
            ],
            'create_url': 'suppliers:supplier_add',
            'create_label': 'Add Supplier',
            'edit_url': 'suppliers:supplier_edit',
            'delete_url': 'suppliers:supplier_delete',
            'empty_message': 'No suppliers found.',
            'query': self.request.GET.get('q', ''),
        })
        return ctx


class SupplierCreateView(RoleRequiredMixin, CreateView):
    required_roles = ('ADMIN', 'CASHIER')
    model = Supplier
    form_class = SupplierForm
    template_name = 'catalog/form.html'
    success_url = reverse_lazy('suppliers:supplier_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Add Supplier',
            'subtitle': 'Register a new supplier',
            'icon': 'user-plus',
            'cancel_url': reverse_lazy('suppliers:supplier_list'),
        })
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Supplier created successfully.')
        return super().form_valid(form)


class SupplierUpdateView(RoleRequiredMixin, UpdateView):
    required_roles = ('ADMIN', 'CASHIER')
    model = Supplier
    form_class = SupplierForm
    template_name = 'catalog/form.html'
    success_url = reverse_lazy('suppliers:supplier_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Edit Supplier',
            'subtitle': 'Update supplier details',
            'icon': 'edit-2',
            'cancel_url': reverse_lazy('suppliers:supplier_list'),
        })
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Supplier updated successfully.')
        return super().form_valid(form)


class SupplierDeleteView(RoleRequiredMixin, DeleteView):
    required_roles = ('ADMIN',)
    model = Supplier
    template_name = 'catalog/confirm_delete.html'
    success_url = reverse_lazy('suppliers:supplier_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Delete Supplier',
            'subtitle': 'Remove this supplier',
            'object_name': 'Supplier',
            'object': self.object.name,
            'cancel_url': reverse_lazy('suppliers:supplier_list'),
        })
        return ctx
