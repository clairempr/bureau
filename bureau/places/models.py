from cities_light.abstract_models import (AbstractCity, AbstractRegion,
                                          AbstractCountry)
from cities_light.receivers import connect_default_signals

from django.db import models


class Country(AbstractCountry):
    pass
connect_default_signals(Country)

class Region(AbstractRegion):
    """
    Extend django-cities-light Region model to keep track of 
    whether or not Freedmen's Bureau was active there
    """
    bureau_operations = models.BooleanField(default=False)
connect_default_signals(Region)

class City(AbstractCity):
    pass
connect_default_signals(City)
