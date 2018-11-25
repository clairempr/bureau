import uuid
from django.db import models

from military.models import Regiment
from places.models import Region

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
    regiments = models.ManyToManyField(
        Regiment,
        related_name='employees',
        related_query_name='employee',
        blank=True,
    )
    bureau_states = models.ManyToManyField(
        Region,
        limit_choices_to={'bureau_operations': True},
        related_name='employees',
        related_query_name='employee',
        blank=True,
    )

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return '{}, {}'.format(self.last_name, self.first_name)

    def save(self, *args, **kwargs):
        # Make sure someone who's a member of a VRC regiment has VRC set to true
        if self.regiments.filter(vrc=True):
            self.vrc = True
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def bureau_state_list(self):
        return '\n'.join([state.name for state in self.bureau_states.all()])







