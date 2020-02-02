from factory import DjangoModelFactory, Faker, SubFactory

from places.models import City, Country, Place, Region


class CountryFactory(DjangoModelFactory):
    """
    Base Country factory
    """

    name = Faker('country')

    class Meta:
        model = Country


class CityFactory(DjangoModelFactory):
    """
    Base City factory
    """

    name = Faker('city')
    country = SubFactory(CountryFactory)

    class Meta:
        model = City


class PlaceFactory(DjangoModelFactory):
    """
    Base Place factory
    """

    class Meta:
        model = Place


class RegionFactory(DjangoModelFactory):
    """
    Base Region factory
    """

    country = SubFactory(CountryFactory)

    class Meta:
        model = Region
