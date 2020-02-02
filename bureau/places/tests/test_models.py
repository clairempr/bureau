from cities_light.exceptions import InvalidItems
from cities_light.settings import ICity, IRegion

from django.test import override_settings, TestCase

from personnel.tests.factories import EmployeeFactory
from places.models import filter_city_import, filter_region_import, set_region_fields
from places.tests.factories import CountryFactory, CountyFactory, RegionFactory


class CountyTestCase(TestCase):
    """
    Test County model
    """

    def test_str(self):
        """
        If County has a state, it should be in __str__
        """

        county = CountyFactory(name='Rowan')
        self.assertTrue(county.country.name in str(county))

        state = RegionFactory()
        county = CountyFactory(name='Rowan', state=state)
        self.assertTrue(county.state.name in str(county))


class ImportTestCase(TestCase):
    """
    Test import of City and Region by cities_light
    """

    @override_settings(LOAD_CITIES_FROM_COUNTRIES=['US',])
    def test_filter_city_import(self):
        """
        filter_city_import() is used by the city_items_pre_import signal to make sure only cities from specified
        countries are loaded by cities_light
        """

        # Loading a city with country code that's in LOAD_CITIES_FROM_COUNTRIES setting should not raise an exception
        items = {ICity.countryCode: 'US'}
        filter_city_import(None, items)

        # Loading a city with country code that's NOT in LOAD_CITIES_FROM_COUNTRIES setting should raise an exception
        items = {ICity.countryCode: 'DE'}
        self.assertRaises(InvalidItems, filter_city_import, None, items)

    @override_settings(LOAD_CITIES_FROM_COUNTRIES=['US',])
    def test_filter_region_import(self):
        """
        filter_region_import() is used by the region_items_pre_import signal to make sure only regions from specified
        countries are loaded by cities_light
        """

        # Loading a region with country code that's in LOAD_CITIES_FROM_COUNTRIES setting should not raise an exception
        items = {IRegion.code: 'USxxx'}
        filter_region_import(None, items)

        # Loading a region with country code that's NOT in LOAD_CITIES_FROM_COUNTRIES setting should raise an exception
        items = {IRegion.code: 'DExxx'}
        self.assertRaises(InvalidItems, filter_region_import, None, items)


class RegionTestCase(TestCase):
    """
    Test Region model
    """

    def test_percent_vrc_employees(self):
        """
        percent_vrc_employees() should return percentage of employees_employed with vrc=True
        """
        state = RegionFactory(name='Sunshine State')

        self.assertEqual(state.percent_vrc_employees(), 0,
                        "Region with no employees should have percent_vrc_employees() 0")

        employee = EmployeeFactory(vrc=False)
        employee.bureau_states.add(state)

        self.assertEqual(state.percent_vrc_employees(), 0,
                        "Region with no VRC employees should have percent_vrc_employees() 0")

        employee = EmployeeFactory(vrc=True)
        employee.bureau_states.add(state)

        self.assertEqual(state.percent_vrc_employees(), 50,
                        "Region with 50% VRC employees should have percent_vrc_employees() 50")
