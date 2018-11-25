import uuid

from django.db import models

from places.models import Region


class Regiment(models.Model):
    """
    Regiment class,
    to enable fine-grained filtering of Bureau employees' military service
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.IntegerField(blank=True)
    name = models.CharField(max_length=100, blank=True)
    state = models.ForeignKey(Region, models.SET_NULL, null=True, blank=True)
    us = models.BooleanField(default=False)
    usct = models.BooleanField(default=False)
    vrc = models.BooleanField(default=False)

    class Meta:
        ordering = ['state', 'vrc', 'us', 'usct', 'number', 'name']

    def __str__(self):
        return self.name

