import uuid

from partial_date import PartialDateField

from django.db import models

from personnel.models import Employee
from places.models import Place


class Position(models.Model):
    """
    Job title in Freedmen's Bureau like Agent, Subassistant Commissioner, etc.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['title', ]

    def __str__(self):
        return self.title

class Assignment(models.Model):
    """
    Freedmen's Bureau assignment
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    position = models.ForeignKey(Position, null=True, blank=True, on_delete=models.PROTECT, related_name='assignments')
    description = models.CharField(max_length=150, blank=True)
    places = models.ManyToManyField(
        Place,
        limit_choices_to={'region__bureau_operations': True},
        related_name='assignments',
        related_query_name='assignment',
        blank=True,
    )

    employee = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.PROTECT, related_name='assignments')
    # Start and end dates use PartialDateField because the entire date isn't usually known
    start_date = PartialDateField(null=True, blank=True)
    end_date = PartialDateField(null=True, blank=True)

    def __str__(self):
        return '{position}, {places}, {start} - {end}'.format(position=self.position, places=self.place_list(),
                                                            start=self.start_date, end=self.end_date)

    def place_list(self):
        return ' and '.join([str(place) for place in self.places.all()])
