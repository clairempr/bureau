from django.urls import path

from bureau.stats.views import (
    general_view,
)

app_name = "stats"
urlpatterns = [
    path("general", view=general_view, name="general"),
]
