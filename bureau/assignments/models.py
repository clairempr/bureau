import uuid

from partial_date import PartialDateField

from django.db import models
from django.db.models import Q

from personnel.models import Employee
from places.models import Place


class Position(models.Model):
    """
    Job title in Freedmen's Bureau like Agent, Subassistant Commissioner, etc.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ['title', ]

    def __str__(self):
        return self.title


class AssignmentManager(models.Manager):

    def during_year(self, year, **kwargs):
        return self.filter(
            Q(start_date__lte='{}'.format(year), end_date__gte='{}'.format(year)) |
            Q(start_date__gte='{}'.format(year)), start_date__lt='{}'.format(year + 1))


class Assignment(models.Model):
    """
    Freedmen's Bureau assignment
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    positions = models.ManyToManyField(
        Position,
        related_name='assignments',
        related_query_name='assignment',
        blank=True,
    )
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

    objects = AssignmentManager()

    def __str__(self):
        return '{positions}, {places}, {start} - {end}'.format(positions=self.position_list(), places=self.place_list(),
                                                               start=self.start_date, end=self.end_date)
    def place_list(self):
        return ' and '.join([str(place) for place in self.places.all()])

    def position_list(self):
        return ' and '.join([str(position) for position in self.positions.all()])
