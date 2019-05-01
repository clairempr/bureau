from django.urls import reverse_lazy
from django.views.generic import ListView, FormView

from places.forms import GeoNamesLookupForm
from places.models import City, County, Region

class BureauStateListView(ListView):

    model = Region
    slug_field = "name"
    slug_url_kwarg = "name"
    template_name = "places/bureau_state_list.html"
    queryset = Region.objects.filter(bureau_operations=True)


bureau_state_list_view = BureauStateListView.as_view()


class GeoNamesLookupBaseView(FormView):

    form_class = GeoNamesLookupForm
    template_name = 'places/geonames_lookup.html'
    geonames_search = None

    def form_valid(self, form):
        self.geonames_search = form.cleaned_data['geonames_search']

        return super().form_valid(form)


class GeoNamesCityLookupView(GeoNamesLookupBaseView):

    def get_success_url(self):
        return reverse_lazy('admin:places_city_add') + '?geonames_search={}'.format(self.geonames_search)


geonames_city_lookup_view = GeoNamesCityLookupView.as_view(extra_context={'lookup_type': 'city'})


class GeoNamesCountyLookupView(GeoNamesLookupBaseView):

    def get_success_url(self):
        return reverse_lazy('admin:places_county_add') + '?geonames_search={}'.format(self.geonames_search)


geonames_county_lookup_view = GeoNamesCountyLookupView.as_view(extra_context={'lookup_type': 'county'})
