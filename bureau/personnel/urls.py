from django.urls import path

from bureau.personnel.views import (
    employee_detail_view,
    employees_born_resided_died_in_place_view,
)

app_name = "personnel"
urlpatterns = [
    path("place/<uuid:place>/", view=employees_born_resided_died_in_place_view,
         name="employees_born_resided_died_in_place"),
    path("<uuid:pk>/", view=employee_detail_view, name="employee_detail"),
]
