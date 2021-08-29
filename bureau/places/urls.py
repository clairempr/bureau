from django.urls import path

from bureau.places.views import (
    bureau_state_detail_view,
    bureau_state_list_view,
    geonames_city_lookup_view,
    geonames_county_lookup_view,
)

app_name = "places"
urlpatterns = [
    path("", view=bureau_state_list_view, name="bureau_state_list"),
    path("<int:pk>/", view=bureau_state_detail_view, name="bureau_state_detail"),
    path("geonames_lookup/city", view=geonames_city_lookup_view, name="geonames_city_lookup"),
    path("geonames_lookup/county", view=geonames_county_lookup_view, name="geonames_county_lookup"),
]
