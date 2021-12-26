from factory import DjangoModelFactory, Faker, LazyAttribute, SubFactory

from places.models import City, Country, County, Place, Region


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



class CountyFactory(DjangoModelFactory):
    """
    Base County factory
    """

    name = Faker('last_name')
    name_ascii = LazyAttribute(lambda obj: obj.name)
    country = SubFactory(CountryFactory)

    class Meta:
        model = County


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

    name = Faker('state')
    country = SubFactory(CountryFactory)

    class Meta:
        model = Region
