from django import forms
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q, Prefetch

from core.mixins import RoleRequiredMixin
from .models import Customer, Measurement
from .forms import CustomerForm, MeasurementForm
from orders.models import Order


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
    required_roles = ('ADMIN', 'CASHIER', 'DESIGNER')
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


class MeasurementListView(RoleRequiredMixin, ListView):
    required_roles = ('ADMIN', 'CASHIER', 'DESIGNER')
    model = Measurement
    template_name = 'catalog/list.html'
    context_object_name = 'measurements'
    paginate_by = 20

    def get_queryset(self):
        qs = Measurement.objects.select_related('customer', 'order').all()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                measurement_id__icontains=q
            ) | qs.filter(customer__full_name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx.update({
            'title': 'Measurements',
            'subtitle': 'Customer body measurement records',
            'icon': 'ruler',
            'object_list': qs,
            'columns': [
                {'header': 'Measurement ID', 'field': 'measurement_id'},
                {'header': 'Customer', 'field': 'customer.full_name'},
                {'header': 'Order', 'field': 'order.order_number'},
                {'header': 'Date', 'field': 'measurement_date'},
            ],
            'create_url': 'customers:measurement_add',
            'create_label': 'Add Measurement',
            'empty_message': 'No measurement records found.',
            'query': self.request.GET.get('q', ''),
        })
        return ctx


class MeasurementCreateView(RoleRequiredMixin, CreateView):
    required_roles = ('ADMIN', 'CASHIER', 'DESIGNER')
    model = Measurement
    form_class = MeasurementForm
    template_name = 'catalog/form.html'

    def dispatch(self, request, *args, **kwargs):
        order_pk = request.GET.get('order')
        self.preselect_order = None
        if order_pk:
            self.preselect_order = get_object_or_404(Order, pk=order_pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.preselect_order:
            return reverse('orders:order_detail', kwargs={'pk': self.preselect_order.pk})
        return reverse_lazy('customers:measurement_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Add Measurement',
            'subtitle': 'Record customer body measurements',
            'icon': 'ruler',
            'cancel_url': self.get_success_url(),
            'preselect_order': self.preselect_order,
        })
        return ctx

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.preselect_order:
            form.fields['customer'].initial = self.preselect_order.customer
            form.fields['customer'].widget = forms.HiddenInput()
            form.fields['order'].initial = self.preselect_order
            form.fields['order'].widget = forms.HiddenInput()
        return form

    def form_valid(self, form):
        if self.preselect_order:
            form.instance.customer = self.preselect_order.customer
            form.instance.order = self.preselect_order
        messages.success(self.request, 'Measurement recorded successfully.')
        return super().form_valid(form)


class CustomerOrdersTableView(RoleRequiredMixin, ListView):
    """
    Tabel pelanggan yang punya custom order, menampilkan ID customer,
    nama, pesanan, dan progress terkini (produksi/desain).
    """
    required_roles = ('ADMIN', 'CASHIER', 'DESIGNER')
    template_name = 'customers/customer_orders.html'
    context_object_name = 'customers_with_orders'
    paginate_by = 20

    def get_queryset(self):
        qs = (
            Customer.objects.filter(custom_orders__isnull=False)
            .distinct()
            .prefetch_related(
                Prefetch(
                    'custom_orders',
                    queryset=Order.objects.select_related('cashier', 'designer')
                        .prefetch_related('productions', 'designs')
                        .order_by('-order_date')
                )
            )
            .order_by('full_name')
        )
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(full_name__icontains=q) |
                Q(customer_id__icontains=q) |
                Q(custom_orders__order_number__icontains=q)
            ).distinct()
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Customer Orders',
            'subtitle': 'Pelanggan dan progress pesanan mereka',
            'icon': 'users',
        })
        return ctx
