from django.views.generic import DetailView, TemplateView

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
