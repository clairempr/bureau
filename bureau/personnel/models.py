import uuid

from partial_date import PartialDateField

from django.db import models
from django.db.models import Q

from medical.models import Ailment
from military.models import Regiment
from places.models import Place, Region


class EmployeeManager(models.Manager):

    def birthplace_known(self, **kwargs):
        return self.exclude(place_of_birth__isnull=True).filter(**kwargs)

    def foreign_born(self, **kwargs):
        return self.birthplace_known().exclude(place_of_birth__country__code2='US').filter(**kwargs)

    def vrc(self, **kwargs):
        return self.filter(vrc=True).filter(**kwargs)

    def non_vrc(self, **kwargs):
        return self.filter(vrc=False).filter(**kwargs)

    def employed_during_year(self, year, **kwargs):
        return self.filter(
            Q(assignments__start_date__lte='{}'.format(year), assignments__end_date__gte='{}'.format(year)) |
            Q(assignments__start_date__gte='{}'.format(year)),
            assignments__start_date__lt='{}'.format(year + 1)).distinct().filter(**kwargs)

class Employee(models.Model):
    """
    Freedmen's Bureau employee, military or civilian, 
    with extra fields for Veteran Reserve Corps service
    """

    # Several Bureau clerks and agents were women. Make it easy to search for them with gender field.
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

    # Dates of birth and death use PartialDateField because often only the year is known
    date_of_birth = PartialDateField(null=True, blank=True)
    place_of_birth = models.ForeignKey(Place, null=True, blank=True, on_delete=models.PROTECT, related_name='employees_born_in')

    # Where was employee living at beginning of the war or when Bureau service started ("appointed from" in Bureau records)
    place_of_residence = models.ForeignKey(Place, null=True, blank=True, on_delete=models.PROTECT, related_name='employees_residing_in')

    date_of_death = PartialDateField(null=True, blank=True)
    place_of_death = models.ForeignKey(Place, null=True, blank=True, on_delete=models.PROTECT,
                                       related_name='employees_died_in')
    # Some employees died during their Bureau assignment
    died_during_assignment = models.BooleanField(default=False)

    notes = models.TextField(blank=True)

    regiments = models.ManyToManyField(
        Regiment,
        related_name='employees',
        related_query_name='employee',
        blank=True,
    )
    bureau_states = models.ManyToManyField(
        Region,
        limit_choices_to={'bureau_operations': True},
        related_name='employees_employed',
        related_query_name='employee_employed',
        blank=True,
    )

    # Keep track of which Bureau employees were considered "colored" because they were underrepresented
    colored = models.BooleanField(default=False)
    # A few Bureau employees were former slaves
    former_slave = models.BooleanField(default=False)

    # Some Bureau employees had been in the Confederate army
    confederate = models.BooleanField(default=False)
    # A few Bureau employees seem to have been slaveholders
    slaveholder = models.BooleanField(default=False)

    # A significant proportion of the Bureau's employees had some sort of physical disability due to
    # war injuries or chronic disease
    ailments = models.ManyToManyField(
        Ailment,
        related_name='employees',
        related_query_name='employee',
        blank=True,
    )

    # A large number were members of the Veteran Reserve Corps
    vrc = models.BooleanField(default=False)
    # Several employees entered William Oland Bourne's Left-Handed Penmanship Contest
    penmanship_contest =  models.BooleanField(default=False)

    # Keep track of which employees have already been backfilled when adding new fields
    needs_backfilling = models.BooleanField(default=False)

    objects = EmployeeManager()

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return '{}, {}'.format(self.last_name, self.first_name)

    def save(self, *args, **kwargs):
        # Make sure someone who's a member of a VRC regiment has VRC set to true
        if self.regiments.filter(vrc=True):
            self.vrc = True
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def age_at_death(self):
        """
        Quick and dirty calculation just using birth and death years, if filled
        """
        if self.date_of_birth and self.date_of_death:
            return self.date_of_death.date.year - self.date_of_birth.date.year
        return None

    def bureau_state_list(self):
        return '\n'.join([state.name for state in self.bureau_states.all()])

    def calculate_age(self, year):
        if self.date_of_birth:
            return year - self.date_of_birth.date.year
        return None







