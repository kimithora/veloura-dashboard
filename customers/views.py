from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from core.mixins import RoleRequiredMixin
from .models import Customer
from .forms import CustomerForm


class CustomerListView(RoleRequiredMixin, ListView):
    required_roles = ('ADMIN', 'CASHIER', 'DESIGNER')
    template_name = 'catalog/list.html'
    context_object_name = 'customers'
    paginate_by = 20

    def get_queryset(self):
        qs = Customer.objects.all()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(full_name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx.update({
            'title': 'Customers',
            'subtitle': 'Manage customer profiles',
            'icon': 'users',
            'object_list': qs,
            'columns': [
                {'header': 'Customer ID', 'field': 'customer_id'},
                {'header': 'Name', 'field': 'full_name'},
                {'header': 'Phone', 'field': 'phone'},
                {'header': 'Email', 'field': 'email'},
                {'header': 'Total Spending', 'field': 'total_spending'},
            ],
            'create_url': 'customers:customer_add',
            'create_label': 'Add Customer',
            'edit_url': 'customers:customer_edit',
            'delete_url': 'customers:customer_delete',
            'empty_message': 'No customers found.',
            'query': self.request.GET.get('q', ''),
        })
        return ctx


class CustomerCreateView(RoleRequiredMixin, CreateView):
    required_roles = ('ADMIN', 'CASHIER')
    model = Customer
    form_class = CustomerForm
    template_name = 'catalog/form.html'
    success_url = reverse_lazy('customers:customer_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Add Customer',
            'subtitle': 'Register a new customer',
            'icon': 'user-plus',
            'cancel_url': reverse_lazy('customers:customer_list'),
        })
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Customer created successfully.')
        return super().form_valid(form)


class CustomerUpdateView(RoleRequiredMixin, UpdateView):
    required_roles = ('ADMIN', 'CASHIER')
    model = Customer
    form_class = CustomerForm
    template_name = 'catalog/form.html'
    success_url = reverse_lazy('customers:customer_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Edit Customer',
            'subtitle': 'Update customer details',
            'icon': 'edit-2',
            'cancel_url': reverse_lazy('customers:customer_list'),
        })
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Customer updated successfully.')
        return super().form_valid(form)


class CustomerDeleteView(RoleRequiredMixin, DeleteView):
    required_roles = ('ADMIN',)
    model = Customer
    template_name = 'catalog/confirm_delete.html'
    success_url = reverse_lazy('customers:customer_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Delete Customer',
            'subtitle': 'Remove this customer',
            'object_name': 'Customer',
            'object': self.object.full_name,
            'cancel_url': reverse_lazy('customers:customer_list'),
        })
        return ctx
