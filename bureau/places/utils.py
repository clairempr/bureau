import json
from urllib.parse import urlencode

import requests

from django.conf import settings

from places.models import Country, Place, Region
from places.settings import GEONAMES_USERNAME


def geonames_county_lookup(geonames_search):
    """
    Get county by doing GeoNames search with feature code 'ADM2'
    """
    return geonames_lookup(geonames_search, ['ADM2'])


def geonames_city_lookup(geonames_search):
    """
    Get city by doing GeoNames search with feature codes defined in settings
    """
    return geonames_lookup(geonames_search, settings.CITIES_LIGHT_INCLUDE_CITY_TYPES)


def geonames_lookup(geonames_search, feature_codes=None):
    """
    Do GeoNames search for search terms and feature codes
    http://www.geonames.org/export/geonames-search.html
    """
    params = urlencode({'q': geonames_search, 'name_equals': geonames_search.split(',')[0], 'maxRows': 1,
                        'username': GEONAMES_USERNAME})

    # Search for multiple feature codes in GeoNames like this: featureCode=PPLC&featureCode=PPLX
    if feature_codes:
        joined_feature_codes = '&'.join([f'featureCode={fc}' for fc in feature_codes])
        params = f'{params}&{joined_feature_codes}'

    response = requests.get(f'http://api.geonames.org/searchJSON?{params}', timeout=5)
    response = json.loads(response.text)

    geonames = response.get('geonames')
    if not geonames:
        return {'alternate_names': response}

    geonames = geonames[0]

    geoname_id = geonames.get('geonameId')
    name = geonames.get('toponymName')
    state = geonames.get('adminName1')
    country = geonames.get('countryName')
    latitude = geonames.get('lat')
    longitude = geonames.get('lng')
    population = geonames.get('population')
    feature_code = geonames.get('fcode')

    try:
        state = Region.objects.get(name=state)
    except Region.DoesNotExist:
        state = None

    try:
        country = Country.objects.get(name=country)
    except Country.DoesNotExist:
        country = None

    result = {
        'display_name': f'{name}, {state}, {country}',
        'name': name,
        'name_ascii': name,
        'region': state,
        'state': state,
        'country': country,
        'geoname_id': geoname_id,
        'latitude': latitude,
        'longitude': longitude,
        'population': population,
        'feature_code': feature_code,
    }

    return result


def get_place_or_none(pk):
    try:
        return Place.objects.get(pk=pk)
    except Place.DoesNotExist:
        pass

    return None
