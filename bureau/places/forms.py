from __future__ import unicode_literals

from django import forms

from places.models import City, Region


class CityForm(forms.ModelForm):
    """
    City model form
    """
    class Meta:
        model = City
        fields = ('id', 'display_name', 'name', 'name_ascii', 'alternate_names', 'region', 'country', 'geoname_id',
                  'latitude', 'longitude', 'population', 'feature_code')

class RegionForm(forms.ModelForm):
    """
    Region model form
    """
    class Meta:
        model = Region
        fields = ('id', 'display_name', 'name', 'name_ascii', 'alternate_names', 'bureau_operations', 'country', 'geoname_id', 'geoname_code', )
