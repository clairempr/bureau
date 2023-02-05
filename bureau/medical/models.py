import uuid

from django.db import models


class AilmentType(models.Model):
    """
    AilmentType class,
    to define subtypes of medical emergencies (illness/injury/none/unknown, etc.)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Ailment(models.Model):
    """
    Ailment class,
    to state the nature of the medical emergency (general debility/fall from horse/loss of eye, etc.)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.ForeignKey(AilmentType, on_delete=models.PROTECT, related_name='ailments')
    name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name
