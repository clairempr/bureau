import uuid

from django.db import models
from django.urls import reverse

from places.models import Region


class Regiment(models.Model):
    """
    Regiment class,
    to enable fine-grained filtering of Bureau employees' military service
    """

    ARTILLERY = 'ART'
    CAVALRY = 'CAV'
    ENGINEERS = 'ENG'
    INFANTRY = 'INF'
    SHARPSHOOTERS = 'SHA'
    BRANCH_CHOICES = (
        (INFANTRY, 'Infantry'),
        (CAVALRY, 'Cavalry'),
        (ARTILLERY, 'Artillery'),
        (ENGINEERS, 'Engineers'),
        (SHARPSHOOTERS, 'Sharpshooters'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.IntegerField(null=True, blank=True)
    branch = models.CharField(
        max_length=3,
        choices=BRANCH_CHOICES,
        default=INFANTRY,
    )
    name = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    state = models.ForeignKey(Region, models.SET_NULL, null=True, blank=True)
    us = models.BooleanField(default=False)
    usct = models.BooleanField(default=False)
    vrc = models.BooleanField(default=False)
    confederate = models.BooleanField(default=False)

    class Meta:
        ordering = ['state', 'vrc', 'us', 'usct', 'number', 'name']

    def __str__(self):
        return self.name
