from django.contrib.admin import site
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from places.admin import CityAdmin, InUseListFilter
from places.models import City
from places.tests.factories import CityFactory, PlaceFactory


class InUseListFilterTestCase(TestCase):
    """
    Test list filter for whether a City is being used in a Place
    """

    def test_lookups(self):
        city_in_a_place = CityFactory(name='Magnolia')
        PlaceFactory(city=city_in_a_place)

        city_not_in_a_place = CityFactory(name='Grenada')

        modeladmin = CityAdmin(City, site)

        request_factory = RequestFactory()
        user = AnonymousUser()

        request = request_factory.get('/')
        request.user = user
        changelist = modeladmin.get_changelist_instance(request)

        # Make sure that Yes and No are present in the list filter
        filter = InUseListFilter(request, params='', model=City, model_admin=CityAdmin)
        expected = [(choice, choice) for choice in ['Yes', 'No']]
        self.assertEqual(sorted(filter.lookup_choices), sorted(expected))

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {city_in_a_place, city_not_in_a_place})

        # Look for cities that are in a Place
        request = request_factory.get('/', {'in_use': 'Yes'})
        request.user = user
        changelist = modeladmin.get_changelist_instance(request)

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {city_in_a_place})

        # Look for cities that are not in a Place
        request = request_factory.get('/', {'in_use': 'No'})
        request.user = user
        changelist = modeladmin.get_changelist_instance(request)

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {city_not_in_a_place})
