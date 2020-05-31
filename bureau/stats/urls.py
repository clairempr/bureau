from django.urls import path

from bureau.stats.views import (
    general_view,
    detailed_view,
    state_comparison_view,
)

app_name = "stats"
urlpatterns = [
    path("general", view=general_view, name="general"),
    path("detailed", view=detailed_view, name="detailed"),
    path("state_comparison", view=state_comparison_view, name="state_comparison"),
]
