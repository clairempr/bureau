from cities_light.admin import CityAdmin as CitiesLightCityAdmin
from cities_light.admin import RegionAdmin as CitiesLightRegionAdmin

from django.contrib import admin

from .forms import CityForm, RegionForm
from .models import City, Place, Region

class CityAdmin(CitiesLightCityAdmin):
    """
    Extend django-cities-light CityAdmin to include more fields
    """
    list_display = CitiesLightCityAdmin.list_display + ('region', 'feature_code')
    list_filter = CitiesLightCityAdmin.list_filter + ('region', 'feature_code')
    readonly_fields = ('id', )
    form = CityForm

admin.site.unregister(City)
admin.site.register(City, CityAdmin)

class RegionAdmin(CitiesLightRegionAdmin):
    """
    Extend django-cities-light RegionAdmin to include custom fields
    """
    list_display = CitiesLightRegionAdmin.list_display + ('bureau_operations',)
    list_filter = CitiesLightRegionAdmin.list_filter + ('bureau_operations',)
    readonly_fields = ('id', )
    form = RegionForm

admin.site.unregister(Region)
admin.site.register(Region, RegionAdmin)


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'city', 'region', 'country')
    list_filter = ('country', 'region', 'city')
    search_fields = ('city', 'region', 'country')
    fields = ('city', 'region', 'country')
    raw_id_fields = ('city', )
    list_per_page = 75
    save_on_top = True

    def save_model(self, request, obj, form, change):
        # Make sure that region and country don't conflict with selected city
        city = form.cleaned_data['city']
        region = form.cleaned_data['region']

        if city:
            obj.region = city.region
            obj.country = city.country
        elif region:
            obj.country = region.country

        super(PlaceAdmin, self).save_model(request, obj, form, change)


admin.site.register(Place, PlaceAdmin)
