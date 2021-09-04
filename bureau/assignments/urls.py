from django.urls import path

from bureau.assignments.views import (
    assignment_list_view,
)

app_name = "assignments"
urlpatterns = [
    path("", view=assignment_list_view, name="assignment_list"),
    path("place/<uuid:place>/", view=assignment_list_view, name="assignment_list"),
]
