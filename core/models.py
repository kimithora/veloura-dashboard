"""
Core base models for the VELOURA Fashion Management System.

Provides an abstract BaseModel with created/updated timestamps that all
domain models should inherit, plus shared utility models.
"""

from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    """
    Abstract base model with automatic created/updated timestamps.
    All business models should inherit from this.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditMixin(models.Model):
    """
    Abstract mixin that records who created and last updated a record.
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="%(class)s_updated",
    )

    class Meta:
        abstract = True
