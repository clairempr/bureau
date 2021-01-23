from django.urls import path

from bureau.personnel.views import (
    employee_detail_view,
)

app_name = "personnel"
urlpatterns = [
    path("<uuid:pk>/", view=employee_detail_view, name="employee_detail"),
]
