from django.views.generic.base import TemplateView

from personnel.models import Employee

class GeneralView(TemplateView):
    template_name = 'stats/general.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee_count'] = Employee.objects.count()
        context['colored_count'] = Employee.objects.filter(colored=True).count()
        context['confederate_count'] = Employee.objects.filter(confederate=True).count()
        context['female_count'] = Employee.objects.filter(gender=Employee.FEMALE).count()
        context['vrc_count'] = Employee.objects.filter(vrc=True).count()

        return context

general_view = GeneralView.as_view()

