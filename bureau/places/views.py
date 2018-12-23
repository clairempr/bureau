from django.views.generic import ListView

from places.models import Region

class BureauStateListView(ListView):

    model = Region
    slug_field = "name"
    slug_url_kwarg = "name"
    template_name = "places/bureau_state_list.html"
    queryset = Region.objects.filter(bureau_operations=True)


bureau_state_list_view = BureauStateListView.as_view()
