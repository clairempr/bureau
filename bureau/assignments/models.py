import uuid

from partial_date import PartialDateField

from django.conf import settings
from django.db import models
from django.db.models import Q

from personnel.models import Employee
from places.models import Place, Region


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

    def in_place(self, place, exact=False, **kwargs):
        """
        Return assignments in a particular place, according to how specific the place is
        """
        # Only return assignments in that exact place (ex. just Alabama, not a city or county in Alabama)
        if exact:
            return self.filter(places=place)

        # Return assignments in that place and in all places in that place
        assignments = self.filter(places__country=place.country)
        if place.region:
            assignments = assignments.filter(places__region=place.region)
        if place.county:
            assignments = assignments.filter(places__county=place.county)
        elif place.city:
            assignments = assignments.filter(places__city=place.city)
        return assignments


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
    # Under which Assistant Commissioner's jurisdiction did this assignment fall?
    bureau_states = models.ManyToManyField(
        Region,
        limit_choices_to={'bureau_operations': True},
        related_name='assignments',
        related_query_name='assignment',
        blank=True,
        verbose_name='bureau states (jurisdiction)'
    )

    employee = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.PROTECT, related_name='assignments')
    # Start and end dates use PartialDateField because the entire date isn't usually known
    start_date = PartialDateField(null=True, blank=True)
    end_date = PartialDateField(null=True, blank=True)
    # This is to distinguish Bureau Headquarters assignments from other assignments in Washington, DC
    bureau_headquarters = models.BooleanField(default=False)

    objects = AssignmentManager()

    def __str__(self):

        # In cases where one of the elements used in __str__() can't be accessed without causing an exception
        # (deleting an inline Assignment in Employee admin, for example), __str__() should return Assignment.description
        try:
            return '{positions}, {places}, {dates}'.format(positions=self.position_list(), places=self.place_list(),
                                                           dates=self.dates())
        except:
            return self.description

    def bureau_state_list(self):
        return ', '.join([state.name for state in self.bureau_states.all()])

    def dates(self):
        # An assignment can have a start date and end date, or just one of those, or none at all
        if self.start_date and self.end_date:
            return '{start} - {end}'.format(start=self.start_date, end=self.end_date)
        elif self.start_date:
            return str(self.start_date)
        elif self.end_date:
            return str(self.end_date)

        return settings.DEFAULT_EMPTY_FIELD_STRING

    def place_list(self):
        if self.places.exists():
            return ' and '.join([place.name_without_country() for place in self.places.all()])

        return settings.DEFAULT_EMPTY_FIELD_STRING

    def position_list(self):
        if self.positions.exists():
            return ' and '.join([str(position) for position in self.positions.all()])

        return settings.DEFAULT_EMPTY_FIELD_STRING
