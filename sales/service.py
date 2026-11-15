from decimal import Decimal

from django.db import transaction as db_transaction
from django.contrib.contenttypes.models import ContentType

from .models import Transaction, TransactionItem
from inventory.models import StockMovement
from catalog.models import ProductVariant


class InsufficientStockError(Exception):
    pass


class TransactionService:
    # Business logic for sales transactions and stock deduction.

    @staticmethod
    def finalize_transaction(cart_items, cashier, customer=None, discount_amount=0, notes=''):
        # Convert a cart into a Transaction + TransactionItems.
        # Stock is NOT deducted here. Starts PENDING / UNPAID.
        subtotal = Decimal('0')
        discount_amount = Decimal(discount_amount or 0)
        for item in cart_items:
            unit_price = Decimal(item['unit_price'])
            qty = int(item['quantity'])
            item_discount = Decimal(item.get('discount', 0) or 0)
            subtotal += unit_price * qty
            discount_amount += item_discount
        grand_total = subtotal - discount_amount

        with db_transaction.atomic():
            tx = Transaction.objects.create(
                cashier=cashier,
                customer=customer,
                subtotal=subtotal,
                discount_amount=discount_amount,
                grand_total=grand_total,
                status=Transaction.Status.PENDING,
                payment_status=Transaction.PaymentStatus.UNPAID,
                notes=notes,
            )
            for item in cart_items:
                variant = ProductVariant.objects.get(pk=item['variant_id'])
                TransactionItem.objects.create(
                    transaction=tx,
                    product_variant=variant,
                    quantity=item['quantity'],
                    unit_price=Decimal(item['unit_price']),
                    discount=Decimal(item.get('discount', 0) or 0),
                )
        return tx

    @staticmethod
    @db_transaction.atomic
    def deduct_stock(tx, user):
        # Deduct stock for a completed transaction.
        # select_for_update locks variant rows to prevent overselling.
        # Idempotent: returns early if stock already deducted.
        if tx.stock_deducted:
            return tx
        if tx.status != Transaction.Status.COMPLETED:
            raise ValueError('Transaction must be COMPLETED before stock deduction.')

        items = tx.items.select_related('product_variant').all()
        variant_ids = [i.product_variant_id for i in items]
        locked = {v.pk: v for v in ProductVariant.objects.select_for_update().filter(pk__in=variant_ids)}

        for item in items:
            variant = locked.get(item.product_variant_id)
            if variant is None:
                raise InsufficientStockError('Variant {} not found.'.format(item.product_variant_id))
            if variant.stock_quantity < item.quantity:
                raise InsufficientStockError(
                    'Insufficient stock for {}: have {}, need {}'.format(
                        variant.sku, variant.stock_quantity, item.quantity
                    )
                )
            previous = variant.stock_quantity
            new_stock = previous - item.quantity
            variant.stock_quantity = new_stock
            variant.save(update_fields=['stock_quantity', 'updated_at'])
            StockMovement.objects.create(
                content_type=ContentType.objects.get_for_model(ProductVariant),
                object_id=variant.pk,
                movement_type=StockMovement.MovementType.SALES,
                quantity=item.quantity,
                previous_stock=previous,
                new_stock=new_stock,
                reference=tx.transaction_number,
                user=user,
                notes='Sale {}'.format(tx.transaction_number),
            )

        tx.stock_deducted = True
        tx.save(update_fields=['stock_deducted', 'updated_at'])
        return tx

    @staticmethod
    def cancel_transaction(tx, user):
        # Cancel a transaction. Restore inventory via RETURN movements if
        # stock was already deducted. Failed/cancelled transactions must not
        # leave inventory deducted.
        with db_transaction.atomic():
            if tx.status == Transaction.Status.CANCELLED:
                return tx
            if tx.stock_deducted:
                items = tx.items.select_related('product_variant').all()
                variant_ids = [i.product_variant_id for i in items]
                locked = {v.pk: v for v in ProductVariant.objects.select_for_update().filter(pk__in=variant_ids)}
                for item in items:
                    variant = locked[item.product_variant_id]
                    previous = variant.stock_quantity
                    new_stock = previous + item.quantity
                    variant.stock_quantity = new_stock
                    variant.save(update_fields=['stock_quantity', 'updated_at'])
                    StockMovement.objects.create(
                        content_type=ContentType.objects.get_for_model(ProductVariant),
                        object_id=variant.pk,
                        movement_type=StockMovement.MovementType.RETURN,
                        quantity=item.quantity,
                        previous_stock=previous,
                        new_stock=new_stock,
                        reference=tx.transaction_number,
                        user=user,
                        notes='Return for cancelled sale {}'.format(tx.transaction_number),
                    )
            tx.status = Transaction.Status.CANCELLED
            tx.payment_status = Transaction.PaymentStatus.REFUNDED
            tx.save(update_fields=['status', 'payment_status', 'updated_at'])
        return tx
