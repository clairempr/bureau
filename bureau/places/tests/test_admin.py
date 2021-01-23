from unittest.mock import patch

from django.contrib.admin import site
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from django.test import RequestFactory, TestCase
from django.urls import reverse

from places.admin import CityAdmin, InUseListFilter, PopulationListFilter
from places.models import City
from places.tests.factories import CityFactory, PlaceFactory


User = get_user_model()


class CityAdminTestCase(TestCase):
    """
    Tests for CityAdmin
    """

    @patch('places.admin.geonames_city_lookup', autospec=True)
    def test_get_changeform_initial_data(self, mock_geonames_city_lookup):
        """
        If request has a GET parameter 'geonames_search', get_changeform_initial_data() should call
        geonames_city_lookup() with those search terms and return the result
        """

        User.objects.create_superuser(username='fred', password='secret', email='email')
        self.client.login(username='fred', password='secret')

        self.client.get(reverse('admin:places_city_add'))
        self.assertEqual(mock_geonames_city_lookup.call_count, 0,
                         "geonames_city_lookup() shouldn't be called if no 'geonames_search' GET parameter supplied")

        self.client.get(reverse('admin:places_city_add'), {'geonames_search': 'Atlanta, Georgia'})
        self.assertEqual(mock_geonames_city_lookup.call_count, 1,
                         "geonames_city_lookup() should be called if 'geonames_search' GET parameter supplied")
        mock_geonames_city_lookup.reset_mock()


class CityAdminListFilterTestCase(TestCase):
    """
    Tests for list filters used in City admin
    """

    def setUp(self):
        self.modeladmin = CityAdmin(City, site)
        self.request_factory = RequestFactory()
        self.user = AnonymousUser()

    def test_in_use(self):
        """
        in_use() should return whether or not a City is used in a Place
        """

        city_in_a_place = CityFactory(name='Magnolia')
        PlaceFactory(city=city_in_a_place)

        city_not_in_a_place = CityFactory(name='Grenada')

        self.assertTrue(self.modeladmin.in_use(city_in_a_place),
                        "CityAdmin.in_use() should return True for City that's in a Place")
        self.assertFalse(self.modeladmin.in_use(city_not_in_a_place),
                         "CityAdmin.in_use() should return False for City that's not in a Place")

    def test_in_use_list_filter(self):
        """
        Test list filter for whether a City is being used in a Place
        """
        parameter = 'in_use'

        city_in_a_place = CityFactory(name='Magnolia')
        PlaceFactory(city=city_in_a_place)

        city_not_in_a_place = CityFactory(name='Grenada')

        request = self.request_factory.get('/')
        request.user = self.user
        changelist = self.modeladmin.get_changelist_instance(request)

        # Make sure that Yes and No are present in the list filter
        filter = InUseListFilter(request, params='', model=City, model_admin=CityAdmin)
        expected = [(choice, choice) for choice in ['Yes', 'No']]
        self.assertEqual(sorted(filter.lookup_choices), sorted(expected))

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {city_in_a_place, city_not_in_a_place})

        # Look for cities that are in a Place
        request = self.request_factory.get('/', {parameter: 'Yes'})
        request.user = self.user
        changelist = self.modeladmin.get_changelist_instance(request)

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {city_in_a_place})

        # Look for cities that are not in a Place
        request = self.request_factory.get('/', {parameter: 'No'})
        request.user = self.user
        changelist = self.modeladmin.get_changelist_instance(request)

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {city_not_in_a_place})


    def test_population_list_filter(self):
        """
        Test list filter for City by population
        """
        parameter = 'population'

        city_with_pop_0 = CityFactory(name='Abbeville', population=0)
        city_with_pop_1 = CityFactory(name='Baltimore', population=1)
        city_with_pop_500 = CityFactory(name='Corinth', population=500)
        city_with_pop_1000 = CityFactory(name='Demopolis', population=1000)
        city_with_pop_15000 = CityFactory(name='Edenton', population=15000)

        request = self.request_factory.get('/')
        request.user = self.user
        changelist = self.modeladmin.get_changelist_instance(request)

        # Make sure that Yes and No are present in the list filter
        filter = PopulationListFilter(request, params='', model=City, model_admin=CityAdmin)
        expected = [(number, label) for (number, label) in zip([1, 500, 1000, 15000],['0', '< 500', '< 1000', '< 15000'])]
        self.assertEqual(sorted(filter.lookup_choices), sorted(expected))

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {city_with_pop_0, city_with_pop_1, city_with_pop_500, city_with_pop_1000,
                                            city_with_pop_15000})

        # Look for cities with population 0
        request = self.request_factory.get('/', {parameter: 1})
        request.user = self.user
        changelist = self.modeladmin.get_changelist_instance(request)

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {city_with_pop_0})

        # Look for cities with population < 500
        request = self.request_factory.get('/', {parameter: 500})
        request.user = self.user
        changelist = self.modeladmin.get_changelist_instance(request)

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {city_with_pop_0, city_with_pop_1})

        # Look for cities with population < 1000
        request = self.request_factory.get('/', {parameter: 1000})
        request.user = self.user
        changelist = self.modeladmin.get_changelist_instance(request)

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {city_with_pop_0, city_with_pop_1, city_with_pop_500})

        # Look for cities with population < 15000
        request = self.request_factory.get('/', {parameter: 15000})
        request.user = self.user
        changelist = self.modeladmin.get_changelist_instance(request)

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {city_with_pop_0, city_with_pop_1, city_with_pop_500, city_with_pop_1000})
