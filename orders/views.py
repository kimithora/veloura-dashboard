from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction as db_transaction

from core.mixins import RoleRequiredMixin
from .models import Order, OrderStatusHistory
from .forms import OrderForm


class OrderListView(RoleRequiredMixin, ListView):
    required_roles = ('ADMIN', 'CASHIER', 'DESIGNER')
    template_name = 'catalog/list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        qs = Order.objects.select_related('customer', 'cashier', 'designer').all()
        if self.request.user.has_role('DESIGNER'):
            qs = qs.filter(designer=self.request.user)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(order_number__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx.update({
            'title': 'Custom Orders',
            'subtitle': 'Manage couture custom orders',
            'icon': 'scissors',
            'object_list': qs,
            'columns': [
                {'header': 'Order #', 'field': 'order_number'},
                {'header': 'Customer', 'field': 'customer.full_name'},
                {'header': 'Cashier', 'field': 'cashier.username'},
                {'header': 'Designer', 'field': 'designer.username'},
                {'header': 'Status', 'field': 'get_status_display'},
                {'header': 'Total', 'field': 'total_amount'},
                {'header': 'Balance', 'field': 'remaining_balance'},
            ],
            'create_url': 'orders:order_add',
            'create_label': 'Add Order',
            'detail_url': 'orders:order_detail',
            'empty_message': 'No custom orders found.',
            'query': self.request.GET.get('q', ''),
        })
        return ctx


class OrderCreateView(RoleRequiredMixin, CreateView):
    required_roles = ('ADMIN', 'CASHIER')
    model = Order
    form_class = OrderForm
    template_name = 'catalog/form.html'
    success_url = reverse_lazy('orders:order_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Add Custom Order',
            'subtitle': 'Create a new couture order',
            'icon': 'user-plus',
            'cancel_url': reverse_lazy('orders:order_list'),
        })
        return ctx

    def form_valid(self, form):
        form.instance.cashier = self.request.user
        messages.success(self.request, 'Custom order created successfully.')
        return super().form_valid(form)


class OrderUpdateView(RoleRequiredMixin, UpdateView):
    required_roles = ('ADMIN', 'CASHIER', 'DESIGNER')
    model = Order
    form_class = OrderForm
    template_name = 'catalog/form.html'
    success_url = reverse_lazy('orders:order_list')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_role('DESIGNER'):
            qs = qs.filter(designer=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Edit Order',
            'subtitle': 'Update order details',
            'icon': 'edit-2',
            'cancel_url': reverse_lazy('orders:order_list'),
        })
        return ctx


class OrderDetailView(RoleRequiredMixin, DetailView):
    required_roles = ('ADMIN', 'CASHIER', 'DESIGNER')
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        qs = Order.objects.select_related('customer', 'cashier', 'designer').all()
        if self.request.user.has_role('DESIGNER'):
            qs = qs.filter(designer=self.request.user)
        return qs


@login_required
@require_POST
def update_order_status(request, pk):
    """Designer/cashier updates order status. Records history."""
    order = get_object_or_404(Order, pk=pk)
    if not request.user.has_role('ADMIN') and not request.user.has_role('CASHIER') and not request.user.has_role('DESIGNER'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    # Designer can only update orders assigned to them.
    if request.user.has_role('DESIGNER') and order.designer_id != request.user.pk:
        return JsonResponse({'error': 'You can only update orders assigned to you.'}, status=403)
    new_status = request.POST.get('status')
    notes = request.POST.get('notes', '')
    if new_status not in dict(Order.Status.choices):
        return JsonResponse({'error': 'Invalid status'}, status=400)
    with db_transaction.atomic():
        old_status = order.status
        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
        OrderStatusHistory.objects.create(
            order=order, status=new_status, changed_by=request.user,
            notes='Changed from {} to {}'.format(old_status, new_status) + (' - ' + notes if notes else ''),
        )
    messages.success(request, 'Order status updated to {}.'.format(order.get_status_display()))
    return JsonResponse({'ok': True, 'new_status': order.get_status_display()})
