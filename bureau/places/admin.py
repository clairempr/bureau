from cities_light.admin import RegionAdmin as CitiesLightRegionAdmin

from django.contrib import admin

from .models import Region

class RegionAdmin(CitiesLightRegionAdmin):
    """
    Extend django-cities-light RegionAdmin to include custom fields
    """
    list_display = CitiesLightRegionAdmin.list_display + ('bureau_operations',)
    list_filter = CitiesLightRegionAdmin.list_filter + ('bureau_operations',)

admin.site.unregister(Region)
admin.site.register(Region, RegionAdmin)
