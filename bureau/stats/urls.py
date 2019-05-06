from django.urls import path

from bureau.stats.views import (
    general_view,
    vrc_view,
)

app_name = "stats"
urlpatterns = [
    path("general", view=general_view, name="general"),
    path("vrc", view=vrc_view, name="vrc"),
]
