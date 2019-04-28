from cities_light.admin import CityAdmin as CitiesLightCityAdmin
from cities_light.admin import RegionAdmin as CitiesLightRegionAdmin

from django.contrib import admin

from .forms import CityForm, RegionForm
from .models import City, County, Place, Region


class InUseListFilter(admin.SimpleListFilter):
    title = 'In use'
    parameter_name = 'in_use'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'Yes':
                return queryset.filter(places__isnull=False)
            elif self.value() == 'No':
                return queryset.filter(places__isnull=True)
        return queryset

class PopulationListFilter(admin.SimpleListFilter):
    title = 'Population'
    parameter_name = 'population'

    def lookups(self, request, model_admin):
        return (
            (1, '0'),
            (500, '< 500'),
            (1000, '< 1000'),
            (15000, '< 15000'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(population__lt=self.value())
        return queryset

class CityAdmin(CitiesLightCityAdmin):
    """
    Extend django-cities-light CityAdmin to include more fields
    """
    list_display = CitiesLightCityAdmin.list_display + ('region', 'feature_code', 'in_use')
    list_filter = CitiesLightCityAdmin.list_filter + ('region', 'feature_code', PopulationListFilter, InUseListFilter)
    search_fields = ('name', )
    readonly_fields = ('id', )
    form = CityForm

    def in_use(self, obj):
        return obj.places.exists()

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


class CountyAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')
    list_filter = ('state', )
    search_fields = ('name', 'state',)
    save_on_top = True


admin.site.register(County, CountyAdmin)


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'city', 'county', 'region', 'country')
    list_filter = ('country', 'region', 'county')
    search_fields = ('city', 'county', 'region', 'country')
    fields = ('id', 'city', 'county', 'region', 'country')
    readonly_fields = ('id', )
    raw_id_fields = ('city', 'county')
    list_per_page = 75
    save_on_top = True

    def save_model(self, request, obj, form, change):
        # Make sure that region and country don't conflict with selected city
        city = form.cleaned_data['city']
        region = form.cleaned_data['region']

        if city:
            obj.region = city.region
            obj.country = city.country
        elif obj.county:
            obj.region = obj.county.state
            obj.country = obj.county.country
        elif region:
            obj.country = region.country

        super(PlaceAdmin, self).save_model(request, obj, form, change)


admin.site.register(Place, PlaceAdmin)
