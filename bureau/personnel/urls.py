from django.urls import path

from bureau.personnel.views import (
    statistics_view,
)

app_name = "personnel"
urlpatterns = [
    path("statistics", view=statistics_view, name="statistics"),
]
