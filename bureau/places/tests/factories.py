from factory import DjangoModelFactory, Faker, SubFactory

from ..models import Country, Region


class CountryFactory(DjangoModelFactory):
    """
    Base Country factory
    """

    name = Faker('country')

    class Meta:
        model = Country


class RegionFactory(DjangoModelFactory):
    """
    Base Region factory
    """

    country = SubFactory(CountryFactory)

    class Meta:
        model = Region
