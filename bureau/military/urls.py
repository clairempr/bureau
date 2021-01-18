from django.urls import path

from bureau.military.views import (
    confederate_regiment_list_view,
    regiment_detail_view,
    regiment_list_view,
    regular_army_regiment_list_view,
    state_regiment_list_view,
    usct_regiment_list_view,
    vrc_regiment_list_view,
)

app_name = "military"
urlpatterns = [
    path("", view=regiment_list_view, name="regiment_list"),
    path("confederate/", view=confederate_regiment_list_view, name="confederate_regiment_list"),
    path("regular/", view=regular_army_regiment_list_view, name="regular_army_regiment_list"),
    path("state/", view=state_regiment_list_view, name="state_regiment_list"),
    path("usct/", view=usct_regiment_list_view, name="usct_regiment_list"),
    path("vrc/", view=vrc_regiment_list_view, name="vrc_regiment_list"),
    path("<uuid:pk>/", view=regiment_detail_view, name="regiment_detail"),
]
