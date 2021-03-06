import os

# States/areas where Freedmen's Bureau carried out operations,
# including what is now Oklahoma (then called Indian Territory or Cherokee Nation)
BUREAU_STATES = [
    'AL',
    'AR',
    'DC',
    'DE',
    'FL',
    'GA',
    'IL',
    'KS',
    'KY',
    'LA',
    'MD',
    'MS',
    'MO',
    'NC',
    'OK',
    'SC',
    'TN',
    'TX',
    'VA',
    'WV',
]

GEONAMES_USERNAME = os.environ.get('GEONAMES_USERNAME', '')

# Sometimes we want to group Germany, Prussia, Bavaria, Hessia, and Saxony, etc. together, because of inconsistencies
# in reporting of German places in the sources
GERMANY_COUNTRY_NAMES = ['Germany', 'Prussia', 'Bavaria', 'Grand Duchy of Baden', 'Hessia', 'Saxony']

# Only load regions from a country when needed
LOAD_REGIONS_FROM_COUNTRIES =  [
    'US',
    'UK',
]

# Many foreign-born Bureau employees have only a country listed, so only load cities from a country when needed
LOAD_CITIES_FROM_COUNTRIES =  [
    'CA',
    'ES',
    'UK',
    'US',
]
