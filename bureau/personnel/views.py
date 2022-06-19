from django.views.generic import DetailView, ListView, TemplateView

from medical.models import Ailment, AilmentType
from personnel.models import Employee
from places.models import Place, Region


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
        else:
            for key in ['first_name', 'last_name', 'gender']:
                value = self.request.GET.get(key, '')
                context[key] = value
            selected_bureau_states = self.request.GET.getlist('bureau_states', [])
            # Checkboxes
            for key in ['vrc', 'union_veteran', 'confederate_veteran']:
                if key in self.request.GET:
                    context[key] = key

        context['bureau_states'] = [(state, True if str(state.pk) in selected_bureau_states else False)
                                    for state in Region.objects.bureau_state()]

        return context

    def get_queryset(self):
        qs = Employee.objects.all()

        # If search criteria have been cleared, just return default queryset
        if self.request.GET.get('clear', False):
            return qs

        # Name
        first_name = self.request.GET.get('first_name')
        if first_name:
            qs = qs.filter(first_name__icontains=first_name)
        last_name = self.request.GET.get('last_name')
        if last_name:
            qs = qs.filter(last_name__icontains=last_name)

        # Gender is "Male" or "Female" in select,  but value in model is "M" or "F"
        gender = self.request.GET.get('gender')
        if gender:
            qs = qs.filter(gender=gender[0])

        # Bureau states
        selected_bureau_states = self.request.GET.getlist('bureau_states', [])
        if selected_bureau_states:
            qs = qs.filter(bureau_states__in=selected_bureau_states)

        # VRC/Union veteran/Confederate veteran
        if 'vrc' in self.request.GET:
            qs = qs.filter(vrc=True)
        if 'union_veteran' in self.request.GET:
            qs = qs.filter(union_veteran=True)
        if 'confederate_veteran' in self.request.GET:
            qs = qs.filter(confederate_veteran=True)

        return qs.distinct()


employee_list_view = EmployeeListView.as_view()


class EmployeesBornResidedDiedInPlaceView(TemplateView):

    model = Employee
    template_name = "personnel/employees_born_resided_died_in_place.html"

    def get_place(self):
        # If place is in kwargs and it's the pk of a Place, return the Place
        # otherwise return None
        place_pk = self.kwargs.get('place')
        if place_pk:
            try:
                return Place.objects.get(pk=place_pk)
            except Place.DoesNotExist:
                pass

        return None

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
