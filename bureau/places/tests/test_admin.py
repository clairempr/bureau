from unittest.mock import patch

from django.contrib.admin import site
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from django.test import RequestFactory, TestCase
from django.urls import reverse

from places.admin import CityAdmin, InUseListFilter, PopulationListFilter
from places.models import City, Place
from places.tests.factories import CityFactory, CountryFactory, CountyFactory, PlaceFactory, RegionFactory


User = get_user_model()


class AdminTestCase(TestCase):
    """
    Base class for testing places Admin
    """

    def setUp(self):
        # Set up superuser to log in to admin
        User.objects.create_superuser(username='fred', password='secret', email='email')
        self.client.login(username='fred', password='secret')


class CityAdminTestCase(AdminTestCase):
    """
    Tests for CityAdmin
    """

    @patch('places.admin.geonames_city_lookup', autospec=True)
    def test_get_changeform_initial_data(self, mock_geonames_city_lookup):
        """
        If request has a GET parameter 'geonames_search', get_changeform_initial_data() should call
        geonames_city_lookup() with those search terms and return the result
        """

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
        list_filter = InUseListFilter(request, params='', model=City, model_admin=CityAdmin)
        expected = [(choice, choice) for choice in ['Yes', 'No']]
        self.assertEqual(sorted(list_filter.lookup_choices), sorted(expected))

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

        # Value is neither Yes nor No (shouldn't happen, but test anyway), should return all cities
        request = self.request_factory.get('/', {parameter: 'Maybe'})
        request.user = self.user
        changelist = self.modeladmin.get_changelist_instance(request)
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), set(City.objects.all()))

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
        list_filter = PopulationListFilter(request, params='', model=City, model_admin=CityAdmin)
        expected = list(zip([1, 500, 1000, 15000], ['0', '< 500', '< 1000', '< 15000']))
        self.assertEqual(sorted(list_filter.lookup_choices), sorted(expected))

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


class CountyAdminTestCase(AdminTestCase):
    """
    Tests for CountyAdmin
    """

    @patch('places.admin.geonames_county_lookup', autospec=True)
    def test_get_changeform_initial_data(self, mock_geonames_county_lookup):
        """
        If request has a GET parameter 'geonames_search', get_changeform_initial_data() should call
        geonames_county_lookup() with those search terms and return the result
        """

        self.client.get(reverse('admin:places_county_add'))
        self.assertEqual(mock_geonames_county_lookup.call_count, 0,
                         "geonames_county_lookup() shouldn't be called if no 'geonames_search' GET parameter supplied")

        self.client.get(reverse('admin:places_county_add'), {'geonames_search': 'Fulton, Georgia'})
        self.assertEqual(mock_geonames_county_lookup.call_count, 1,
                         "geonames_county_lookup() should be called if 'geonames_search' GET parameter supplied")
        mock_geonames_county_lookup.reset_mock()


class PlaceAdminTestCase(AdminTestCase):
    """
    Tests for PlaceAdmin
    """

    def test_save_model(self):
        """
        save_model() should make sure that region and country don't conflict with selected city
        """

        url = reverse('admin:places_place_add')

        city = CityFactory()
        county = CountyFactory()
        region = RegionFactory()
        country = CountryFactory()

        # Keep track of pks of Places after they're created, to be able to retrieve the Place that has just been created
        existing_places_pks = []

        # If city is supplied, Place should be assigned the region and country of that city
        self.client.post(url,
                         {'id': 1, 'city': city.id, 'region': region.id, 'country': country.id},
                         follow=True,)
        place = Place.objects.last()
        existing_places_pks.append(place.pk)
        self.assertEqual(place.region, city.region,
                         "PlaceAdmin.save_model() should get Place's region from its city.region")
        self.assertEqual(place.country, city.country,
                         "PlaceAdmin.save_model() should get Place's country from its city.country")

        # If county is supplied (and not city), Place should be assigned the state and country of that county
        self.client.post(url,
                         {'id': 2, 'county': county.id, 'region': region.id, 'country': country.id},
                         follow=True, )
        place = Place.objects.exclude(pk__in=existing_places_pks).last()
        existing_places_pks.append(place.pk)
        self.assertEqual(place.region, county.state,
                         "PlaceAdmin.save_model() should get Place's region from its county.state")
        self.assertEqual(place.country, county.country,
                         "PlaceAdmin.save_model() should get Place's country from its county.country")

        # If region is supplied (and not city or county), Place should be assigned the country of that region
        self.client.post(url,
                         {'id': 3, 'region': region.id, 'country': country.id},
                         follow=True, )
        place = Place.objects.exclude(pk__in=existing_places_pks).last()
        existing_places_pks.append(place.pk)
        self.assertEqual(place.country, region.country,
                         "PlaceAdmin.save_model() should get Place's country from its region.country")

        # If no city, county, or region is supplied, nothing should change about the Place
        self.client.post(url,
                         {'id': 4, 'country': country.id},
                         follow=True, )
        place = Place.objects.exclude(pk__in=existing_places_pks).last()
        existing_places_pks.append(place.pk)
        self.assertEqual(place.country, country,
                         "PlaceAdmin.save_model() should get keep Place's country if no city, county, or region set")
