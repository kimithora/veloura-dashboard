"""
Accounts app models.

Defines Role and a custom User model used across the VELOURA system.
Three roles: ADMIN, CASHIER, DESIGNER.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class Role(models.Model):
    """
    System role. Controls access to dashboards and features.
    """
    class Code(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        CASHIER = 'CASHIER', 'Cashier'
        DESIGNER = 'DESIGNER', 'Designer'

    code = models.CharField(max_length=20, choices=Code.choices, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Custom user model. Extends Django's AbstractUser with a role and contact info.
    Email is used as the unique identifier where applicable, but username remains
    the Django authentication identifier for simplicity.
    """
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r'^\+?\d{7,15}$', 'Enter a valid phone number.')],
    )
    address = models.TextField(blank=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='users',
        help_text='Role determines dashboard and feature access.',
    )
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into the admin site.',
    )

    class Meta:
        ordering = ['username']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    @property
    def role_code(self):
        return self.role.code if self.role else None

    def has_role(self, code):
        return self.role is not None and self.role.code == code

    def can_access(self, *codes):
        return self.role is not None and self.role.code in codes
