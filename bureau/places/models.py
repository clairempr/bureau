from cities_light.abstract_models import (AbstractCity, AbstractRegion,
                                          AbstractCountry)
from cities_light.receivers import connect_default_signals
from cities_light.signals import region_items_post_import

from django.db import models

from .settings import BUREAU_STATES


class City(AbstractCity):
    pass
connect_default_signals(City)

class Region(AbstractRegion):
    """
    Extend django-cities-light Region model to keep track of 
    whether or not Freedmen's Bureau was active there
    """
    bureau_operations = models.BooleanField(default=False)

    def percent_vrc_employees(self):
        total = self.employees.count()
        return self.employees.filter(vrc=True).count() / total * 100 if total else 0

connect_default_signals(Region)


# Signal to set bureau_operations to True in selected states post-import
def set_region_fields(sender, instance, items, **kwargs):
    if instance.geoname_code in BUREAU_STATES:
        instance.bureau_operations = True
region_items_post_import.connect(set_region_fields)


class Country(AbstractCountry):
    pass
connect_default_signals(Country)
