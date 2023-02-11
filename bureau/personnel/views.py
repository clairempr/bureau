import datetime

from django.db.models import Q
from django.views.generic import DetailView, ListView, TemplateView

from medical.models import Ailment, AilmentType
from personnel.models import Employee
from places.models import Region
from places.settings import GERMANY_COUNTRY_NAMES
from places.utils import get_place_or_none


class EmployeeDetailView(DetailView):

    model = Employee


employee_detail_view = EmployeeDetailView.as_view()


class EmployeeListView(ListView):

    model = Employee
    paginate_by = 25
    slug_field = "name"
    slug_url_kwarg = "name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # If search criteria haven't been cleared,
        # put values in context so they can be used to re-populate search form
        if self.request.GET.get('clear', False):
            selected_bureau_states = []
            selected_ailments = []
        else:
            for key in ['first_name', 'last_name', 'gender', 'place_of_birth', 'year_of_birth_start',
                        'year_of_birth_end', 'place_of_death']:
                value = self.request.GET.get(key, '')
                context[key] = value

            # Multiselect
            selected_bureau_states = self.request.GET.getlist('bureau_states', [])
            selected_ailments = self.request.GET.getlist('ailments', [])

            # Checkboxes
            for key in ['vrc', 'union_veteran', 'confederate_veteran', 'colored', 'died_during_assignment',
                        'former_slave', 'slaveholder']:
                if key in self.request.GET:
                    context[key] = key

        context['bureau_states'] = [(state, str(state.pk) in selected_bureau_states)
                                    for state in Region.objects.bureau_state()]
        context['ailments'] = [(ailment, str(ailment.pk) in selected_ailments)
                               for ailment in Ailment.objects.all()]

        return context

    def get_queryset(self):
        # pylint: disable=too-many-branches
        qs = Employee.objects.all()

        # If search criteria have been cleared, just return default queryset
        if self.request.GET.get('clear', False):
            return qs

        # Booleans from checkboxes
        if 'died_during_assignment' in self.request.GET:
            qs = qs.filter(died_during_assignment=True)
        if 'vrc' in self.request.GET:
            qs = qs.filter(vrc=True)
        if 'union_veteran' in self.request.GET:
            qs = qs.filter(union_veteran=True)
        if 'confederate_veteran' in self.request.GET:
            qs = qs.filter(confederate_veteran=True)
        if 'colored' in self.request.GET:
            qs = qs.filter(colored=True)
        if 'former_slave' in self.request.GET:
            qs = qs.filter(former_slave=True)
        if 'slaveholder' in self.request.GET:
            qs = qs.filter(slaveholder=True)

        # Gender is "Male" or "Female" in select,  but value in model is "M" or "F"
        gender = self.request.GET.get('gender')
        if gender:
            qs = qs.filter(gender=gender[0])

        # Fields with search text
        first_name = self.request.GET.get('first_name')
        if first_name:
            qs = qs.filter(first_name__icontains=first_name)
        last_name = self.request.GET.get('last_name')
        if last_name:
            qs = qs.filter(last_name__icontains=last_name)
        place_of_birth = self.request.GET.get('place_of_birth')
        if place_of_birth:
            qs = self.filter_place_of_birth(qs, place_of_birth)
        place_of_death = self.request.GET.get('place_of_death')
        if place_of_death:
            qs = self.filter_place_of_death(qs, place_of_death)

        # PartialDate fields can't be filtered with Django query
        year_of_birth_start = self.request.GET.get('year_of_birth_start')
        if year_of_birth_start:
            filtered_pks = [employee.pk for employee in qs.filter(date_of_birth__isnull=False) if
                            employee.date_of_birth.date >= datetime.date(int(year_of_birth_start), 1, 1)]
            qs = Employee.objects.filter(pk__in=filtered_pks)
        year_of_birth_end = self.request.GET.get('year_of_birth_end')
        if year_of_birth_end:
            filtered_pks = [employee.pk for employee in qs.filter(date_of_birth__isnull=False) if
                            employee.date_of_birth.date <= datetime.date(int(year_of_birth_end), 12, 31)]
            qs = Employee.objects.filter(pk__in=filtered_pks)

        # Bureau states
        selected_bureau_states = self.request.GET.getlist('bureau_states', [])
        if selected_bureau_states:
            qs = qs.filter(bureau_states__in=selected_bureau_states)
        # Ailments
        selected_ailments = self.request.GET.getlist('ailments', [])
        if selected_ailments:
            qs = qs.filter(ailments__in=selected_ailments)

        return qs.distinct()

    def filter_place_of_birth(self, qs, place_of_birth):
        # Group Germany, Prussia, Bavaria, and Saxony, etc. together, because of inconsistencies in reporting of
        # German places in the sources
        if place_of_birth.upper() == 'GERMANY':
            return qs.filter(place_of_birth__country__name__in=GERMANY_COUNTRY_NAMES)

        return qs.filter(Q(place_of_birth__country__name__icontains=place_of_birth)
                         | Q(place_of_birth__region__name__icontains=place_of_birth)
                         | Q(place_of_birth__county__name__icontains=place_of_birth)
                         | Q(place_of_birth__city__name__icontains=place_of_birth))

    def filter_place_of_death(self, qs, place_of_death):
        # Group Germany, Prussia, Bavaria, and Saxony, etc. together, because of inconsistencies in reporting of
        # German places in the sources
        if place_of_death.upper() == 'GERMANY':
            return qs.filter(place_of_death__country__name__in=GERMANY_COUNTRY_NAMES)
        # Virginia and West Virginia shouldn't be grouped together, because West Virginia was already a state
        # when the war ended
        if place_of_death.upper() == 'VIRGINIA':
            return qs.filter(place_of_death__region__name__iexact=place_of_death)
        return qs.filter(Q(place_of_death__country__name__icontains=place_of_death)
                         | Q(place_of_death__region__name__icontains=place_of_death)
                         | Q(place_of_death__county__name__icontains=place_of_death)
                         | Q(place_of_death__city__name__icontains=place_of_death))


employee_list_view = EmployeeListView.as_view()


class EmployeesBornResidedDiedInPlaceView(TemplateView):

    model = Employee
    template_name = "personnel/employees_born_resided_died_in_place.html"

    def get_place(self):
        # If place is in kwargs, try to return the Place
        place_pk = self.kwargs.get('place')
        return get_place_or_none(place_pk) if place_pk else None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Put the specified Place object in the view context. If there wasn't one, it will be None
        place = self.get_place()
        context['place'] = place

        if place:
            context['employees_born_in_place'] = Employee.objects.born_in_place(place=place)
            context['employees_resided_in_place'] = Employee.objects.resided_in_place(place=place)
            context['employees_died_in_place'] = Employee.objects.died_in_place(place=place)

        return context


employees_born_resided_died_in_place_view = EmployeesBornResidedDiedInPlaceView.as_view()


class EmployeesWithAilmentListView(ListView):
    """
    If ailment specified, list all employees with that ailment,
    otherwise if ailment_type specified, list all employees with that ailment type
    """

    model = Employee
    paginate_by = 25
    queryset = Employee.objects.all()
    template_name = "personnel/employees_with_ailment_list.html"

    def get_ailment(self):
        # If ailment is in kwargs and it's the pk of an Ailment, return the Ailment
        # otherwise return None
        ailment_pk = self.kwargs.get('ailment')
        if ailment_pk:
            try:
                return Ailment.objects.get(pk=ailment_pk)
            except Ailment.DoesNotExist:
                pass

        return None

    def get_ailment_type(self):
        # If ailment_type is in kwargs and it's the pk of an AilmentType, return the AilmentType
        # otherwise return None
        ailment_type_pk = self.kwargs.get('ailment_type')
        if ailment_type_pk:
            try:
                return AilmentType.objects.get(pk=ailment_type_pk)
            except AilmentType.DoesNotExist:
                pass

        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ailment = self.get_ailment()

        if ailment:
            context['ailment'] = ailment
        else:
            context['ailment'] = self.get_ailment_type()

        return context

    def get_queryset(self):
        ailment = self.get_ailment()
        if ailment:
            return self.queryset.filter(ailments=ailment)

        ailment_type = self.get_ailment_type()
        if ailment_type:
            return self.queryset.filter(ailments__type=ailment_type)

        return self.queryset


employees_with_ailment_list_view = EmployeesWithAilmentListView.as_view()
