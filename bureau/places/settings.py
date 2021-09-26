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
GERMANY_COUNTRY_NAME = 'Germany'
GERMANY_COUNTRY_NAMES = [GERMANY_COUNTRY_NAME, 'Prussia', 'Bavaria', 'Grand Duchy of Baden', 'Hessia', 'Saxony']

# Sometimes Virginia and West Virginia need to be grouped together, because of inconsistencies in reporting
# birthplaces in the sources, and because all employees were born before West Virginia was formed
VIRGINIA_REGION_NAME = 'Virginia'
VIRGINIA_REGION_NAMES = [VIRGINIA_REGION_NAME, 'West Virginia']

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
