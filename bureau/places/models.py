import uuid

from cities_light.abstract_models import (AbstractCity, AbstractRegion,
                                          AbstractCountry)
from cities_light.exceptions import InvalidItems
from cities_light.receivers import connect_default_signals
from cities_light.settings import ICity, IRegion
from cities_light.signals import city_items_pre_import, region_items_pre_import, region_items_post_import

from django.core.exceptions import ValidationError
from django.db import models

from .settings import BUREAU_STATES, LOAD_CITIES_FROM_COUNTRIES, LOAD_REGIONS_FROM_COUNTRIES


class City(AbstractCity):
    pass

connect_default_signals(City)

# Signal to import only cities from certain countries
def filter_city_import(sender, items, **kwargs):
    if items[ICity.countryCode] not in LOAD_CITIES_FROM_COUNTRIES:
        raise InvalidItems()

city_items_pre_import.connect(filter_city_import)


class RegionManager(models.Manager):

    def bureau_state(self, **kwargs):
        return self.filter(bureau_operations=True).filter(**kwargs)


class Region(AbstractRegion):
    """
    Extend django-cities-light Region model to keep track of
    whether or not Freedmen's Bureau was active there
    """
    bureau_operations = models.BooleanField(default=False)

    objects = RegionManager()

    def percent_vrc_employees(self):
        total = self.employees_employed.count()
        return self.employees_employed.filter(vrc=True).count() / total * 100 if total else 0

connect_default_signals(Region)

# Signal to import only regions from certain countries
def filter_region_import(sender, items, **kwargs):
    if items[IRegion.code][:2] not in LOAD_REGIONS_FROM_COUNTRIES:
        raise InvalidItems()

region_items_pre_import.connect(filter_region_import)

# Signal to set bureau_operations to True in selected states post-import
def set_region_fields(sender, instance, items, **kwargs):
    if instance.country == 'US' and instance.geoname_code in BUREAU_STATES:
        instance.bureau_operations = True

region_items_post_import.connect(set_region_fields)

class County(AbstractRegion):
    """
    Counties (regions with feature code 'ADM2' aren't supported by django-cities-light
    and they're sometimes needed for birthplaces and Bureau assignments
    """

    state = models.ForeignKey(Region, null=True, blank=True, on_delete=models.PROTECT, related_name='counties')


    class Meta(Region.Meta):
        unique_together = ('country', 'state', 'name')
        verbose_name = ('county')
        verbose_name_plural = ('counties')

    def __str__(self):
        """
        Not all counties (Irish, for example) will have a state set
        """
        if self.state:
            return '{name}, {state}, {country}'.format(name=self.name, state=self.state.name, country=self.country.name)
        return '{name}, {country}'.format(name=self.name, country=self.country.name)


class Country(AbstractCountry):
    pass
connect_default_signals(Country)


class Place(models.Model):
    """
    Place with city and region optional
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.PROTECT, related_name='places')
    county = models.ForeignKey(County, null=True, blank=True, on_delete=models.PROTECT, related_name='places')
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.PROTECT, related_name='places')
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.PROTECT, related_name='places')


    class Meta:
        unique_together = ('city', 'region', 'country')

    def __str__(self):
        if self.city:
            return str(self.city)
        elif self.county:
            return str(self.county)
        elif self.region:
            return str(self.region)
        return str(self.country)

    def name_without_country(self):
        # Return place name without country, unless place consists of only a country
        name = str(self)

        country_suffix = ', {}'.format(str(self.country))
        if self.region and name.endswith(country_suffix):
            name = name[:-len(country_suffix)]

        return name

    def clean(self):
        super().clean()
        if not (self.city or self.county or self.region or self.country):
            raise ValidationError('This is absolutely nowhere. Fill at least one field.')


    def save(self, *args, **kwargs):
        # Make sure that region and country don't conflict with selected city
        if self.city:
            self.region = self.city.region
            self.country = self.city.country
        elif self.county:
            self.region = self.county.state
            self.country = self.county.country
        elif self.region:
            self.country = self.region.country

        super().save(*args, **kwargs)  # Call the "real" save() method.
