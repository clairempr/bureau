from django.views.generic import ListView

from military.models import Regiment

class RegimentListView(ListView):

    model = Regiment
    slug_field = "name"
    slug_url_kwarg = "name"


regiment_list_view = RegimentListView.as_view()
