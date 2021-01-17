from django.urls import path

from bureau.military.views import (
    regiment_detail_view,
    regiment_list_view,
    vrc_regiment_list_view,
)

app_name = "military"
urlpatterns = [
    path("", view=regiment_list_view, name="regiment_list"),
    path("vrc/", view=vrc_regiment_list_view, name="vrc_regiment_list"),
    path("<uuid:pk>/", view=regiment_detail_view, name="regiment_detail"),
]
