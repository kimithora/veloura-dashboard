from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings

from core.models import BaseModel, AuditMixin
from sales.models import Transaction


class Payment(BaseModel, AuditMixin):
    class Method(models.TextChoices):
        CASH = 'CASH', 'Cash'
        BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'
        QRIS = 'QRIS', 'QRIS'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Confirmation'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        REFUNDED = 'REFUNDED', 'Refunded'
        FAILED = 'FAILED', 'Failed'

    class PaymentType(models.TextChoices):
        FULL = 'FULL', 'Full Payment'
        DP = 'DP', 'Down Payment (DP)'
        INSTALLMENT = 'INSTALLMENT', 'Installment'

    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name='payments'
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    payment_type = models.CharField(
        max_length=16, choices=PaymentType.choices, default=PaymentType.FULL,
    )
    method = models.CharField(max_length=20, choices=Method.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_proof = models.FileField(upload_to='payment_proofs/', blank=True, null=True)
    due_date = models.DateField(null=True, blank=True, help_text='Jatuh tempo untuk cicilan/DP.')
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='confirmed_payments',
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        indexes = [
            models.Index(fields=['transaction', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_type']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return '{} - {} - {}'.format(self.transaction.transaction_number, self.amount, self.status)

    @property
    def is_confirmed(self):
        return self.status == self.Status.CONFIRMED
