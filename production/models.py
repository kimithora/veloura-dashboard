from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings

from core.models import BaseModel, AuditMixin
from inventory.models import Material
from orders.models import Order


class Production(BaseModel, AuditMixin):
    """
    Production record for a custom order.
    """

    class Status(models.TextChoices):
        PLANNED = 'PLANNED', 'Planned'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        ON_HOLD = 'ON_HOLD', 'On Hold'
        COMPLETED = 'COMPLETED', 'Completed'
        DELAYED = 'DELAYED', 'Delayed'

    production_id = models.CharField(max_length=32, unique=True, blank=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='productions'
    )
    designer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='productions',
    )
    start_date = models.DateField(null=True, blank=True)
    estimated_completion = models.DateField(null=True, blank=True)
    actual_completion = models.DateField(null=True, blank=True)
    progress = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0)],
        help_text='Percentage 0-100.',
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PLANNED
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Production'
        verbose_name_plural = 'Productions'
        indexes = [
            models.Index(fields=['production_id']),
            models.Index(fields=['status', '-created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.production_id:
            last = Production.objects.order_by('-production_id').first()
            num = 1
            if last and last.production_id and last.production_id.startswith('PRD-'):
                try:
                    num = int(last.production_id.split('-')[1]) + 1
                except (ValueError, IndexError):
                    num = 1
            self.production_id = 'PRD-{:04d}'.format(num)
        super().save(*args, **kwargs)

    def __str__(self):
        return '{} - {}'.format(self.production_id, self.order.order_number)


class MaterialRequest(BaseModel, AuditMixin):
    """
    Designer requests raw/supporting materials from inventory.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        FULFILLED = 'FULFILLED', 'Fulfilled'
        REJECTED = 'REJECTED', 'Rejected'

    request_id = models.CharField(max_length=32, unique=True, blank=True)
    production = models.ForeignKey(
        Production, on_delete=models.CASCADE, related_name='material_requests'
    )
    material = models.ForeignKey(
        Material, on_delete=models.PROTECT, related_name='requests'
    )
    quantity = models.DecimalField(
        max_digits=12, decimal_places=3, validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='material_requests',
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_material_requests',
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Material Request'
        verbose_name_plural = 'Material Requests'
        indexes = [
            models.Index(fields=['request_id']),
            models.Index(fields=['status', '-created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.request_id:
            last = MaterialRequest.objects.order_by('-request_id').first()
            num = 1
            if last and last.request_id and last.request_id.startswith('REQ-'):
                try:
                    num = int(last.request_id.split('-')[1]) + 1
                except (ValueError, IndexError):
                    num = 1
            self.request_id = 'REQ-{:04d}'.format(num)
        super().save(*args, **kwargs)

    def __str__(self):
        return '{} - {}'.format(self.request_id, self.material.name)


class MaterialUsage(BaseModel, AuditMixin):
    """
    Actual material usage recorded when materials are consumed in production.
    Creates a StockMovement (PRODUCTION_USAGE).
    """

    usage_id = models.CharField(max_length=32, unique=True, blank=True)
    production = models.ForeignKey(
        Production, on_delete=models.CASCADE, related_name='material_usages'
    )
    material_request = models.ForeignKey(
        MaterialRequest, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='usages',
    )
    material = models.ForeignKey(
        Material, on_delete=models.PROTECT, related_name='usages'
    )
    quantity_used = models.DecimalField(
        max_digits=12, decimal_places=3, validators=[MinValueValidator(0)]
    )
    used_at = models.DateTimeField(auto_now_add=True)
    used_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='material_usages',
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-used_at']
        verbose_name = 'Material Usage'
        verbose_name_plural = 'Material Usages'
        indexes = [
            models.Index(fields=['usage_id']),
            models.Index(fields=['production', '-used_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.usage_id:
            last = MaterialUsage.objects.order_by('-usage_id').first()
            num = 1
            if last and last.usage_id and last.usage_id.startswith('USG-'):
                try:
                    num = int(last.usage_id.split('-')[1]) + 1
                except (ValueError, IndexError):
                    num = 1
            self.usage_id = 'USG-{:04d}'.format(num)
        super().save(*args, **kwargs)

    def __str__(self):
        return '{} - {}'.format(self.usage_id, self.material.name)


class Fitting(BaseModel, AuditMixin):
    """
    Fitting session linked to a custom order.
    """

    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    fitting_id = models.CharField(max_length=32, unique=True, blank=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='fittings'
    )
    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.CASCADE, related_name='fittings'
    )
    scheduled_date = models.DateTimeField()
    fitting_date = models.DateTimeField(null=True, blank=True)
    results = models.TextField(blank=True, help_text='Fitting results/notes.')
    alterations_required = models.TextField(blank=True)
    documentation = models.FileField(upload_to='fittings/docs/', blank=True, null=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.SCHEDULED
    )

    class Meta:
        ordering = ['-scheduled_date']
        verbose_name = 'Fitting'
        verbose_name_plural = 'Fittings'
        indexes = [
            models.Index(fields=['fitting_id']),
            models.Index(fields=['status', '-scheduled_date']),
        ]

    def save(self, *args, **kwargs):
        if not self.fitting_id:
            last = Fitting.objects.order_by('-fitting_id').first()
            num = 1
            if last and last.fitting_id and last.fitting_id.startswith('FIT-'):
                try:
                    num = int(last.fitting_id.split('-')[1]) + 1
                except (ValueError, IndexError):
                    num = 1
            self.fitting_id = 'FIT-{:04d}'.format(num)
        super().save(*args, **kwargs)

    def __str__(self):
        return '{} - {}'.format(self.fitting_id, self.order.order_number)


class QualityControl(BaseModel, AuditMixin):
    """
    Quality control checklist for an order.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PASSED = 'PASSED', 'Passed'
        FAILED = 'FAILED', 'Failed'
        REQUIRES_REVISION = 'REQUIRES_REVISION', 'Requires Revision'

    qc_id = models.CharField(max_length=32, unique=True, blank=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='quality_controls'
    )
    stitching_quality = models.BooleanField(default=False)
    size_accuracy = models.BooleanField(default=False)
    fabric_quality = models.BooleanField(default=False)
    color_consistency = models.BooleanField(default=False)
    design_conformity = models.BooleanField(default=False)
    cleanliness = models.BooleanField(default=False)
    final_appearance = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    qc_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='qc_checks',
    )
    qc_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Quality Control'
        verbose_name_plural = 'Quality Controls'
        indexes = [
            models.Index(fields=['qc_id']),
            models.Index(fields=['status', '-created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.qc_id:
            last = QualityControl.objects.order_by('-qc_id').first()
            num = 1
            if last and last.qc_id and last.qc_id.startswith('QC-'):
                try:
                    num = int(last.qc_id.split('-')[1]) + 1
                except (ValueError, IndexError):
                    num = 1
            self.qc_id = 'QC-{:04d}'.format(num)
        super().save(*args, **kwargs)

    @property
    def all_checks_passed(self):
        return all([
            self.stitching_quality, self.size_accuracy, self.fabric_quality,
            self.color_consistency, self.design_conformity, self.cleanliness,
            self.final_appearance,
        ])

    def __str__(self):
        return '{} - {}'.format(self.qc_id, self.order.order_number)
