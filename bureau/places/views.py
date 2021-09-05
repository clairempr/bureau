from django.db.models import Case, CharField, F, When
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView

from assignments.models import Assignment
from places.forms import GeoNamesLookupForm
from places.models import City, County, Place, Region

class BureauStateListView(ListView):

    model = Region
    slug_field = "name"
    slug_url_kwarg = "name"
    template_name = "places/bureau_state_list.html"
    queryset = Region.objects.bureau_state()


bureau_state_list_view = BureauStateListView.as_view()

class BureauStateDetailView(DetailView):

    model = Region
    template_name = "places/bureau_state_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Return a list of places in that state where there was an assignment, ordering by
        #   1) State only
        #   2) Cities and counties together, sorted alphabetically
        #
        # Bureau Headquarters is tricky because it's not a real place. Assignments could be in Washington, DC
        # but District of Columbia assignments are also there
        #
        place = Place.objects.get(region=self.object, city=None, county=None)
        assignment_list = Assignment.objects.in_place(place)
        annotated_assignment_places_list = Place.objects.filter(assignment__in=assignment_list).distinct().annotate(
            annotated_name=Case(
                When(county__name__isnull=False, then=F('county__name')),
                When(city__name__isnull=False, then=F('city__name')),
                output_field=CharField())
        )
        context['assignment_places'] = annotated_assignment_places_list.order_by(F('annotated_name').asc(
            nulls_first=True))

        return context


bureau_state_detail_view = BureauStateDetailView.as_view()


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
