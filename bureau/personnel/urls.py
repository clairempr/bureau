from django.urls import path

from bureau.personnel.views import (
    employee_detail_view,
    employee_list_view,
    employees_born_resided_died_in_place_view,
    employees_with_ailment_list_view,
)

app_name = "personnel"
urlpatterns = [
    path("employees/", view=employee_list_view, name="employee_list"),
    path("ailment/<uuid:ailment>/", view=employees_with_ailment_list_view,
         name="employees_with_ailment_list"),
    path("ailment_type/<uuid:ailment_type>/", view=employees_with_ailment_list_view,
         name="employees_with_ailment_type_list"),
    path("place/<uuid:place>/", view=employees_born_resided_died_in_place_view,
         name="employees_born_resided_died_in_place"),
    path("<uuid:pk>/", view=employee_detail_view, name="employee_detail"),
]
