from django.views.generic import DetailView, ListView, TemplateView

from medical.models import Ailment, AilmentType
from personnel.models import Employee
from places.models import Place


class EmployeeDetailView(DetailView):

    model = Employee


employee_detail_view = EmployeeDetailView.as_view()


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
