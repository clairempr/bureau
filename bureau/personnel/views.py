from django.views.generic import DetailView

from personnel.models import Employee


class EmployeeDetailView(DetailView):

    model = Employee


employee_detail_view = EmployeeDetailView.as_view()
