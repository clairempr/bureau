import json

from unittest.mock import Mock, patch

from django.conf import settings
from django.test import override_settings, TestCase

from places.tests.factories import CountryFactory, RegionFactory
from places.utils import geonames_city_lookup, geonames_county_lookup, geonames_lookup


class GeonamesLookupTestCase(TestCase):
    """
    Tests for GeoNames lookups
    """

    @patch('places.utils.geonames_lookup', autospec=True)
    def test_geonames_city_lookup(self, mock_geonames_lookup):
        """
        geonames_city_lookup() should call geonames_lookup() with search text
         and feature codes from CITIES_LIGHT_INCLUDE_CITY_TYPES setting
        """
        search_text = 'Atlanta, GA'
        geonames_city_lookup(search_text)
        mock_geonames_lookup.assert_called_with(search_text, settings.CITIES_LIGHT_INCLUDE_CITY_TYPES)

    @patch('places.utils.geonames_lookup', autospec=True)
    def test_geonames_county_lookup(self, mock_geonames_lookup):
        """
        geonames_county_lookup() should call geonames_lookup() with search text and feature code 'ADM2'
        """
        search_text = 'Wake, NC'
        geonames_county_lookup(search_text)
        mock_geonames_lookup.assert_called_with(search_text, ['ADM2'])

    @override_settings(GEONAMES_USERNAME='test_username')
    def test_geonames_lookup(self):
        """
        geonames_lookup() should call requests.get()
        """
        state = RegionFactory(name='Arkansas', country=CountryFactory(name='United States'))
        search_text = 'Hamburg, Arkansas'

        response_content = {
            "totalResultsCount": 1,
            "geonames": [{"adminCode1": "AR", "lng": "-91.79763", "geonameId": 4113607, "toponymName": "Hamburg",
                          "countryId": "6252001", "fcl": "P", "population": 2791, "countryCode": "US",
                          "name": "Hamburg",
                          "fclName": "city, village,...", "adminCodes1": {"ISO3166_2": "AR"},
                          "countryName": "United States", "fcodeName": "seat of a second-order administrative division",
                          "adminName1": "Arkansas", "lat": "33.22818", "fcode": "PPLA2"}]
        }

        with patch('requests.get', autospec=True,
                   return_value=Mock(text=json.dumps(response_content), status_code=200)) as mock_requests_get:
            result = geonames_lookup(search_text, feature_codes=settings.CITIES_LIGHT_INCLUDE_CITY_TYPES)
            self.assertEqual(result['name'], 'Hamburg')
            self.assertEqual(result['state'], state)
            # request to GeoNames API should've been sent with feature codes in the params
            args, kwargs = mock_requests_get.call_args
            for feature_code in settings.CITIES_LIGHT_INCLUDE_CITY_TYPES:
                param = 'featureCode={}'.format(feature_code)
                self.assertTrue(param in args[0], "GeoNames API request should include '{}'".format(param))

        # If nothing was found (no 'geonames' in response, response should be returned to the 'alternate_names'field
        response_content = {
            "totalResultsCount": 0,
        }

        with patch('requests.get', autospec=True,
                   return_value=Mock(text=json.dumps(response_content), status_code=200)):
            result = geonames_lookup(search_text, feature_codes=settings.CITIES_LIGHT_INCLUDE_CITY_TYPES)
            self.assertNotIn('name', result)
            self.assertNotIn('state', result)
            self.assertEqual(result['alternate_names'], response_content)

        # If no feature codes passed to geonames_lookup(), then none should be included in the GeoNames API request
        with patch('requests.get', autospec=True,
                   return_value=Mock(text=json.dumps(response_content), status_code=200)) as mock_requests_get:
            geonames_lookup(search_text)
            # request to GeoNames API should've been sent with no feature codes in the params
            args, kwargs = mock_requests_get.call_args
            self.assertFalse('featureCode' in args[0],
                             "GeoNames API request shouldn't include feature codes if none passed to geonames_lookup()")
