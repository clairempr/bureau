from cities_light.exceptions import InvalidItems
from cities_light.settings import ICity, IRegion

from django.core.exceptions import ValidationError
from django.test import override_settings, TestCase

from personnel.tests.factories import EmployeeFactory
from places.models import filter_city_import, filter_region_import, set_region_fields
from places.tests.factories import CityFactory, CountryFactory, CountyFactory, PlaceFactory, RegionFactory


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

    @override_settings(BUREAU_STATES=['AL', 'ENG'])
    def test_set_region_fields(self):
        """
        set_region_fields() is used by the region_items_post_import signal to set bureau_operations to True in
        regions where country is "US" and geoname_code is listed in BUREAU_STATES setting
        """
        us = CountryFactory(code2='US')
        alabama = RegionFactory(country=us, geoname_code='AL', name='Alabama')
        vermont = RegionFactory(country=us, geoname_code='VT', name='Vermont')

        uk = CountryFactory(code2='GB')
        england = RegionFactory(country=uk, geoname_code='ENG', name='England')

        # State in BUREAU_STATES list should get bureau_operations set to True
        set_region_fields(sender=None, instance=alabama, items={})
        self.assertTrue(alabama.bureau_operations,
                        'State in BUREAU_STATES list should get bureau_operations set to True')

        # State not in BUREAU_STATES list shouldn't get bureau_operations set to True
        set_region_fields(sender=None, instance=vermont, items={})
        self.assertFalse(vermont.bureau_operations,
                        "State not in BUREAU_STATES list shouldn't get bureau_operations set to True")

        # Region not in US shouldn't get bureau_operations set to True
        set_region_fields(sender=None, instance=england, items={})
        self.assertFalse(england.bureau_operations,
                        "Region not in US shouldn't get bureau_operations set to True")


class PlaceTestCase(TestCase):
    """
    Test Place model
    """

    def test_str(self):
        """
        If Place has a city, county, or region defined, it should be used in __str__, otherwise country should be used
        """

        city = CityFactory(name='Jonesboro')
        county = CountyFactory(name='Clayton')
        region = RegionFactory(name='Georgia')
        country = CountryFactory(code2='US')

        self.assertEqual(str(PlaceFactory(city=city)), str(city),
                         'If Place has a city defined, str(place) should be str(city)')
        self.assertEqual(str(PlaceFactory(county=county)), str(county),
                         'If Place has a county defined, str(place) should be str(county)')
        self.assertEqual(str(PlaceFactory(region=region)), str(region),
                         'If Place has a region defined, str(place) should be str(region)')
        self.assertEqual(str(PlaceFactory(country=country)), str(country),
                         'If Place has only a country defined, str(place) should be str(country)')

    def test_name_without_country(self):
        """
        name_without_country() should return place name without country, if place has a region defined
        """

        # If place has a region defined, name_without_country() shouldn't include country name
        us = CountryFactory(name='United States')
        georgia = RegionFactory(name='Georgia', country=us)
        jonesboro = CityFactory(name='Jonesboro', region=georgia, country=us)

        self.assertFalse(str(us) in PlaceFactory(city=jonesboro).name_without_country(),
                         "Place.name_without_country() shouldn't include country name if region defined")

        # If place has no region defined, name_without_country() should include country name
        bohemia = CountryFactory(name='Bohemia')
        neuhaus = CityFactory(name='Neuhaus', country=bohemia)

        self.assertTrue(str(bohemia) in str(PlaceFactory(city=neuhaus)),
                        'Place.name_without_country() should include country name if no region defined')

    def test_clean(self):
        """
        clean() should make sure that either city, county, region, or country is filled
        """

        # When Place has no city, county, region, or country, a ValidationError should be raised
        self.assertRaises(ValidationError, PlaceFactory().clean)

        # When place has a city, no error should be raised
        PlaceFactory(city=CityFactory(), county=None, region=None, country=None).clean()

        # When place has a county, no error should be raised
        PlaceFactory(county=CountyFactory(), city=None, region=None, country=None).clean()

        # When place has a region, no error should be raised
        PlaceFactory(region=RegionFactory(), city=None, county=None, country=None).clean()

        # When place has a country, no error should be raised
        PlaceFactory(country=CountryFactory(), city=None, county=None, region=None).clean()

    def test_save(self):
        """
        save() should make sure that region and country don't conflict with selected city
        """

        city = CityFactory()
        county = CountyFactory()
        region = RegionFactory()
        country = CountryFactory()

        # If city is supplied, Place should be assigned the region and country of that city
        place = PlaceFactory(city=city, region=region, country=country)
        self.assertEqual(place.region, city.region,
                         "Place.save() should get Place's region from its city.region")
        self.assertEqual(place.country, city.country,
                         "Place.save() should get Place's country from its city.country")

        # If county is supplied (and not city), Place should be assigned the state and country of that county
        place = PlaceFactory(county=county, region=region, country=country)
        self.assertEqual(place.region, county.state,
                         "Place.save() should get Place's region from its county.state")
        self.assertEqual(place.country, county.country,
                         "Place.save() should get Place's country from its county.country")

        # If region is supplied (and not city or county), Place should be assigned the country of that region
        place = PlaceFactory(region=region, country=country)
        self.assertEqual(place.country, region.country,
                         "Place.save() should get Place's country from its region.country")


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
