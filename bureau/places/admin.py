from cities_light.admin import CityAdmin as CitiesLightCityAdmin
from cities_light.admin import RegionAdmin as CitiesLightRegionAdmin

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .forms import CityForm, CountyForm, RegionForm
from .models import City, County, Place, Region
from .utils import geonames_city_lookup, geonames_county_lookup


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
    readonly_fields = ('id','geonames_lookup' )
    form = CityForm

    def get_changeform_initial_data(self, request):
        geonames_search = request.GET.get('geonames_search')
        if geonames_search:
            return geonames_city_lookup(geonames_search)

        return {}

    def get_fields(self, request, obj=None):
        return ['geonames_lookup',] + super(CityAdmin, self).get_fields(request, obj)

    def in_use(self, obj):
        return obj.places.exists()

    def geonames_lookup(self, obj):
        return format_html(
            '<a class="button" href="{}">Search</a>',
            reverse('places:geonames_city_lookup'),
        )
    geonames_lookup.short_description = 'Lookup in GeoNames'
    geonames_lookup.allow_tags = True

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
    search_fields = ('name', 'state__name',)
    readonly_fields = ('id', 'geonames_lookup')
    form = CountyForm
    save_on_top = True

    def get_changeform_initial_data(self, request):
        geonames_search = request.GET.get('geonames_search')
        if geonames_search:
            return geonames_county_lookup(geonames_search)

        return {}

    def get_fields(self, request, obj=None):
        return ['geonames_lookup',] + super(CountyAdmin, self).get_fields(request, obj)

    def geonames_lookup(self, obj):
        return format_html(
            '<a class="button" href="{}">Search</a>',
            reverse('places:geonames_county_lookup'),
        )
    geonames_lookup.short_description = 'Lookup in GeoNames'
    geonames_lookup.allow_tags = True


admin.site.register(County, CountyAdmin)


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'city', 'county', 'region', 'country')
    list_filter = ( 'region__bureau_operations', 'country', 'region', )
    search_fields = ('city__name', 'county__name', 'region__name', 'country__name')
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
