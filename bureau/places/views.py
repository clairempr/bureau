from django.db.models import Case, CharField, F, When
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView

from assignments.models import Assignment
from medical.models import AilmentType
from personnel.models import Employee
from places.forms import GeoNamesLookupForm
from places.models import City, County, Place, Region
from stats.utils import get_ages_at_death, get_ages_in_year, get_mean, get_median, get_percent

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
        assignment_list = ()

        try:
            place = Place.objects.get(region=self.object, city=None, county=None)
        except Place.DoesNotExist:
            place = None

        if place:
            assignment_list = Assignment.objects.in_place(place)
        elif self.object.bureau_headquarters:
            assignment_list = Assignment.objects.filter(bureau_headquarters=True)

        annotated_assignment_places_list = Place.objects.filter(assignment__in=assignment_list).distinct().annotate(
            annotated_name=Case(
                When(county__name__isnull=False, then=F('county__name')),
                When(city__name__isnull=False, then=F('city__name')), output_field=CharField())
            )
        context['assignment_places'] = annotated_assignment_places_list.order_by(F('annotated_name').asc(
            nulls_first=True))
        context['stats'] = self.get_stats()

        return context

    def get_stats(self):
        """
        Get employee statistics for that state
        """
        employees = self.object.employees_employed.all()
        total_employees = employees.count()

        birthplace_known_count = Employee.objects.birthplace_known(bureau_states=self.object).count()
        born_in_state_count = get_number_employees_born_in_bureau_state(employees, self.object)
        colored_count = employees.filter(colored=True).count()
        confederate_count = employees.filter(confederate_veteran=True).count()
        died_during_assignment_count = employees.filter(died_during_assignment=True).count()
        female_count = employees.filter(gender=Employee.FEMALE).count()
        foreign_born_count = Employee.objects.foreign_born(bureau_states=self.object).count()
        former_slave_count = employees.filter(former_slave=True).count()
        former_slaveholder_count = employees.filter(slaveholder=True).count()
        penmanship_contest_count = employees.filter(penmanship_contest=True).count()
        union_count = employees.filter(union_veteran=True).count()
        usct_count = Employee.objects.usct(bureau_states=self.object).count()

        # Employees with date of birth filled
        employees_with_dob = employees.exclude(date_of_birth='')
        # Age in 1865
        ages = get_ages_in_year(employees_with_dob, 1865)

        stats = [
            ('Avg. age in 1865', get_float_format(get_mean(ages), places=1)),
            ('Median age in 1865', get_float_format(get_median(ages), places=0)),
            ('% VRC', get_float_format(self.object.percent_vrc_employees())),
            ('% USCT', get_float_format(get_percent(part=usct_count, total=total_employees))),
            ('% Foreign-born', get_float_format(get_percent(part=foreign_born_count, total=birthplace_known_count))),
            ('% Born there', get_float_format(get_percent(part=born_in_state_count, total=birthplace_known_count))),
            ('% Female', get_float_format(get_percent(part=female_count, total=total_employees))),
            ('% Identified as "colored"', get_float_format(get_percent(part=colored_count, total=total_employees))),
            ('% Died during assignment', get_float_format(get_percent(part=died_during_assignment_count,
                                                                      total=total_employees))),
            ('Former slaves', former_slave_count),
            ('% Former slaveholder', get_float_format(get_percent(part=former_slaveholder_count,
                                                                  total=total_employees))),
            ('% Union veterans', get_float_format(get_percent(part=union_count, total=total_employees))),

            ('% Confederate veterans', get_float_format(get_percent(part=confederate_count, total=total_employees))),
            ('Left-hand penmanship contest entrants', penmanship_contest_count),
        ]

        # Breakdown per AilmentType
        for ailment_type in AilmentType.objects.all():
            ailment_type_count = employees.filter(ailments__type=ailment_type).count()
            stats.append(('% with {}'.format(str(ailment_type)),
                          get_float_format(get_percent(part=ailment_type_count, total=total_employees))))

            # Breakdown per Ailment, if more than one for the type
            if ailment_type.ailments.count() > 1:
                for ailment in ailment_type.ailments.all():
                    ailment_count = employees.filter(ailments=ailment).count()
                    stats.append(('% with {}'.format(str(ailment)),
                                  get_float_format(get_percent(part=ailment_count, total=total_employees))))

        return stats


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

def get_number_employees_born_in_bureau_state(employees, bureau_state):
    """
    Return the number of state's employees born in that state,
    using District of Columbia as the birthplace for Bureau Headquarters
    """
    state = bureau_state

    if bureau_state.bureau_headquarters:
        try:
            state = Region.objects.get(name__icontains='District of Columbia')
        except Region.DoesNotExist:
            pass

    return employees.filter(place_of_birth__region__id=state.id).count()

def get_float_format(number, places=2):
    """
    Return number with specific float formatting
    """
    format_string = '{:.' + str(places) + 'f}'
    return format_string.format(number) if number % 100 else number
