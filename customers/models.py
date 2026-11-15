from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings

from core.models import BaseModel, AuditMixin


class Customer(BaseModel, AuditMixin):
    """
    Customer profile. Linked to a user account when the customer also has
    login access; otherwise standalone.
    """

    class Source(models.TextChoices):
        WALK_IN = 'WALK_IN', 'Walk-in'
        ONLINE = 'ONLINE', 'Online'
        REFERRAL = 'REFERRAL', 'Referral'

    customer_id = models.CharField(max_length=32, unique=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='customer_profiles',
        help_text='Optional linked user account.',
    )
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    source = models.CharField(max_length=16, choices=Source.choices, default=Source.WALK_IN)
    total_spending = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        indexes = [
            models.Index(fields=['customer_id']),
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
        ]

    def save(self, *args, **kwargs):
        if not self.customer_id:
            # Simple sequential customer id; generated on first save.
            last = Customer.objects.order_by('-customer_id').first()
            num = 1
            if last and last.customer_id and last.customer_id.startswith('CUST-'):
                try:
                    num = int(last.customer_id.split('-')[1]) + 1
                except (ValueError, IndexError):
                    num = 1
            self.customer_id = 'CUST-{:04d}'.format(num)
        super().save(*args, **kwargs)

    def __str__(self):
        return '{} - {}'.format(self.customer_id, self.full_name)

    @property
    def purchase_count(self):
        from sales.models import Transaction
        return Transaction.objects.filter(customer=self).count()


class Measurement(BaseModel, AuditMixin):
    """
    Customer measurement record. Supports multiple records per customer
    and linking to a specific custom order.
    """

    measurement_id = models.CharField(max_length=32, unique=True, blank=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='measurements'
    )
    measurement_date = models.DateField(auto_now_add=True)
    order = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='measurements',
        help_text='Link this measurement to a custom order (optional).',
    )
    chest_circumference = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(0)],
        help_text='In cm.',
    )
    waist_circumference = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(0)],
        help_text='In cm.',
    )
    hip_circumference = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(0)],
        help_text='In cm.',
    )
    shoulder_width = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(0)],
        help_text='In cm.',
    )
    sleeve_length = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(0)],
        help_text='In cm.',
    )
    arm_circumference = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(0)],
        help_text='In cm.',
    )
    neck_circumference = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(0)],
        help_text='In cm.',
    )
    garment_length = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(0)],
        help_text='In cm.',
    )
    skirt_trouser_length = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(0)],
        help_text='In cm.',
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-measurement_date']
        verbose_name = 'Measurement'
        verbose_name_plural = 'Measurements'
        indexes = [
            models.Index(fields=['measurement_id']),
            models.Index(fields=['customer', '-measurement_date']),
            models.Index(fields=['order']),
        ]

    def save(self, *args, **kwargs):
        if not self.measurement_id:
            last = Measurement.objects.order_by('-measurement_id').first()
            num = 1
            if last and last.measurement_id and last.measurement_id.startswith('MEA-'):
                try:
                    num = int(last.measurement_id.split('-')[1]) + 1
                except (ValueError, IndexError):
                    num = 1
            self.measurement_id = 'MEA-{:04d}'.format(num)
        super().save(*args, **kwargs)

    def __str__(self):
        return '{} - {} - {}'.format(self.measurement_id, self.customer.full_name, self.measurement_date)
