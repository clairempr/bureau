import json

from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase

from .factories import CountryFactory, RegionFactory
from ..utils import geonames_city_lookup, geonames_county_lookup, geonames_lookup


class GeonamesLookupTestCase(TestCase):
    """
    Tests for GeoNames lookups
    """

    @patch('bureau.places.utils.geonames_lookup', autospec=True)
    def test_geonames_city_lookup(self, mock_geonames_lookup):
        """
        geonames_city_lookup() should call geonames_lookup() with search text
         and feature codes from CITIES_LIGHT_INCLUDE_CITY_TYPES setting
        """
        search_text = 'Atlanta, GA'
        geonames_city_lookup(search_text)
        mock_geonames_lookup.assert_called_with(search_text, settings.CITIES_LIGHT_INCLUDE_CITY_TYPES)

    @patch('bureau.places.utils.geonames_lookup', autospec=True)
    def test_geonames_county_lookup(self, mock_geonames_lookup):
        """
        geonames_county_lookup() should call geonames_lookup() with search text and feature code 'ADM2'
        """
        search_text = 'Wake, NC'
        geonames_county_lookup(search_text)
        mock_geonames_lookup.assert_called_with(search_text, ['ADM2'])

    def test_geonames_lookup(self):
        """
        geonames_lookup() should call requests.get()
        """
        response_content = {
            "totalResultsCount": 1,
            "geonames": [{"adminCode1": "AR", "lng": "-91.79763", "geonameId": 4113607, "toponymName": "Hamburg",
                          "countryId": "6252001", "fcl": "P", "population": 2791, "countryCode": "US",
                          "name": "Hamburg",
                          "fclName": "city, village,...", "adminCodes1": {"ISO3166_2": "AR"},
                          "countryName": "United States", "fcodeName": "seat of a second-order administrative division",
                          "adminName1": "Arkansas", "lat": "33.22818", "fcode": "PPLA2"}]
        }

        state = RegionFactory(name='Arkansas', country=CountryFactory(name='United States'))
        search_text = 'Hamburg, Arkansas'

        with patch('requests.get', autospec=True,
                   return_value=Mock(text=json.dumps(response_content), status_code=200)):
            result = geonames_lookup(search_text, feature_codes=settings.CITIES_LIGHT_INCLUDE_CITY_TYPES)
            self.assertEqual(result['name'], 'Hamburg')
            self.assertEqual(result['state'], state)
