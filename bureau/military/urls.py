from django.urls import path

from bureau.military.views import (
    regiment_list_view,
)

app_name = "military"
urlpatterns = [
    path("", view=regiment_list_view, name="regiment_list"),
]
