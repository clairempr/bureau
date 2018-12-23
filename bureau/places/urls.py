from django.urls import path

from bureau.places.views import (
    bureau_state_list_view,
)

app_name = "places"
urlpatterns = [
    path("", view=bureau_state_list_view, name="bureau_state_list"),
]
