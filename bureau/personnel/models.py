from cities_light.models import Region

import uuid
from django.db import models


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


class Employee(models.Model):
    """
    Freedmen's Bureau employee, military or civilian, 
    with extra fields for Veteran Reserve Corps service
    """

    # Several Bureau clerks were women. Make it easy to search for them with gender field.
    FEMALE = 'F'
    MALE = 'M'
    GENDER_CHOICES = (
        (FEMALE, 'Female'),
        (MALE, 'Male'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    last_name = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1,choices=GENDER_CHOICES,default=MALE)
    notes = models.TextField(blank=True)
    vrc = models.BooleanField(default=False)
    vrc_units = models.ManyToManyField(
        Regiment,
        related_name="employees",
        related_query_name="employee",
    )
    bureau_states = models.ManyToManyField(
        Region,
        related_name="employees",
        related_query_name="employee",
    )





