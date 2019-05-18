import statistics

from django.views.generic.base import TemplateView

from medical.models import Ailment
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


class VRCView(TemplateView):
    template_name = 'stats/vrc.html'

    def get_context_data(self, **kwargs):
        employees_with_dob = Employee.objects.exclude(date_of_birth='')

        ages_vrc = list(map(lambda x: x.calculate_age(1865), employees_with_dob.filter(vrc=True)))
        ages_non_vrc = list(map(lambda x: x.calculate_age(1865), employees_with_dob.filter(vrc=False)))
        ages_everyone = ages_vrc + ages_non_vrc

        average_age ={'vrc': statistics.mean(ages_vrc),
                      'non_vrc': statistics.mean(ages_non_vrc),
                      'everyone': statistics.mean(ages_everyone) }

        median_age = {'vrc': statistics.median(ages_vrc),
                      'non_vrc': statistics.median(ages_non_vrc),
                      'everyone': statistics.median(ages_everyone)}

        foreign_born_vrc = Employee.objects.foreign_born(vrc=True).count()
        foreign_born_non_vrc = Employee.objects.foreign_born(vrc=False).count()
        foreign_born = {'vrc': foreign_born_vrc / Employee.objects.birthplace_known(vrc=True).count() * 100,
                        'non_vrc': foreign_born_non_vrc / Employee.objects.birthplace_known(vrc=False).count() * 100,
                        'everyone': (foreign_born_vrc + foreign_born_non_vrc) / Employee.objects.birthplace_known().count() * 100}

        employee_count = Employee.objects.count()
        ailments = [{'name': ailment.name,
                     'vrc': Employee.objects.vrc(ailments=ailment).count() / Employee.objects.vrc().count() * 100,
                     'non_vrc': Employee.objects.non_vrc(ailments=ailment).count() / Employee.objects.non_vrc().count() * 100,
                     'everyone': Employee.objects.filter(ailments=ailment).count() / employee_count * 100} for
                    ailment in Ailment.objects.all()]

        context = super().get_context_data(**kwargs)
        context['average_age'] = average_age
        context['median_age'] = median_age
        context['foreign_born'] = foreign_born
        context['ailments'] = ailments
        return context


vrc_view = VRCView.as_view()


