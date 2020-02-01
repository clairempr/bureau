from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from ..utils import geonames_city_lookup, geonames_county_lookup


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
