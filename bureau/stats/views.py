import statistics

from django.db.models import Count
from django.views.generic.base import TemplateView

from medical.models import Ailment
from personnel.models import Employee
from places.models import Place

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


class DetailedView(TemplateView):
    template_name = 'stats/detailed.html'

    def get_context_data(self, **kwargs):
        employee_count = Employee.objects.count()

        # Employees with date of birth filled
        employees_with_dob = Employee.objects.exclude(date_of_birth='')
        # Employees with date of death filled
        employees_with_dob_and_dod = Employee.objects.exclude(date_of_death='').exclude(date_of_birth='')


        # Age in 1865
        ages_vrc = calculate_ages_in_year(employees_with_dob.filter(vrc=True), 1865)
        ages_non_vrc = calculate_ages_in_year(employees_with_dob.filter(vrc=False), 1865)
        ages_usct = calculate_ages_in_year(employees_with_dob.intersection(Employee.objects.usct()), 1865)
        ages_everyone = ages_vrc + ages_non_vrc

        average_age_in_1865 ={'vrc': statistics.mean(ages_vrc),
                      'non_vrc': statistics.mean(ages_non_vrc),
                      'usct': statistics.mean(ages_usct),
                      'everyone': statistics.mean(ages_everyone) }

        median_age_in_1865 = {'vrc': statistics.median(ages_vrc),
                      'non_vrc': statistics.median(ages_non_vrc),
                      'usct': statistics.median(ages_usct),
                      'everyone': statistics.median(ages_everyone)}

        # Age at time of death
        ages_vrc_at_death = calculate_ages_at_death(employees_with_dob_and_dod.filter(vrc=True))
        ages_non_vrc_at_death = calculate_ages_at_death(employees_with_dob_and_dod.filter(vrc=False))
        ages_usct_at_death = calculate_ages_at_death(employees_with_dob_and_dod.intersection(Employee.objects.usct()))
        ages_everyone_at_death = ages_vrc_at_death + ages_non_vrc_at_death

        average_age_at_death ={'vrc': statistics.mean(ages_vrc_at_death),
                      'non_vrc': statistics.mean(ages_non_vrc_at_death),
                      'usct': statistics.mean(ages_usct_at_death),
                      'everyone': statistics.mean(ages_everyone_at_death) }

        median_age_at_death = {'vrc': statistics.median(ages_vrc_at_death),
                      'non_vrc': statistics.median(ages_non_vrc_at_death),
                      'usct': statistics.median(ages_usct_at_death),
                      'everyone': statistics.median(ages_everyone_at_death)}

        # Foreign born
        foreign_born_vrc = Employee.objects.foreign_born(vrc=True).count()
        foreign_born_non_vrc = Employee.objects.foreign_born(vrc=False).count()
        foreign_born_usct = Employee.objects.foreign_born().intersection(Employee.objects.usct()).count()
        foreign_born = {'vrc': foreign_born_vrc / Employee.objects.birthplace_known(vrc=True).count() * 100,
                        'non_vrc': foreign_born_non_vrc / Employee.objects.birthplace_known(vrc=False).count() * 100,
                        'usct': foreign_born_usct / Employee.objects.birthplace_known().intersection(
                            Employee.objects.usct()).count() * 100,
                        'everyone': (foreign_born_vrc + foreign_born_non_vrc) / Employee.objects.birthplace_known().count() * 100}

        # Top places where employees were born
        top_birthplaces = Place.objects.values('region__name', 'country__name').annotate(
            num_employees=Count('employees_born_in')).order_by('-num_employees')[:25]

        # Ailments
        ailments = [{'name': ailment.name,
                     'vrc': Employee.objects.vrc(ailments=ailment).count() / Employee.objects.vrc().count() * 100,
                     'non_vrc': Employee.objects.non_vrc(ailments=ailment).count() / Employee.objects.non_vrc().count() * 100,
                     'usct': Employee.objects.usct(ailments=ailment).count() / Employee.objects.usct().count() * 100,
                     'everyone': Employee.objects.filter(ailments=ailment).count() / employee_count * 100} for
                    ailment in Ailment.objects.all()]
        ailments.append({'name': 'None',
                     'vrc': Employee.objects.vrc(ailments=None).count() / Employee.objects.vrc().count() * 100,
                     'non_vrc': Employee.objects.non_vrc(ailments=None).count() / Employee.objects.non_vrc().count() * 100,
                     'usct': Employee.objects.usct(ailments=None).count() / Employee.objects.usct().count() * 100,
                     'everyone': Employee.objects.filter(ailments=None).count() / employee_count * 100})

        context = super().get_context_data(**kwargs)
        context['average_age_in_1865'] = average_age_in_1865
        context['median_age_in_1865'] = median_age_in_1865
        context['average_age_at_death'] = average_age_at_death
        context['median_age_at_death'] = median_age_at_death
        context['foreign_born'] = foreign_born
        context['top_birthplaces'] = top_birthplaces
        context['ailments'] = ailments
        return context


detailed_view = DetailedView.as_view()


def calculate_ages_at_death(employees):
    """
    Calculate approximate age at death for employees
    Assumes that they have a birth year and death year filled
    """
    return list(map(lambda x: x.age_at_death(), employees))

def calculate_ages_in_year(employees, year):
    """
    Calculate approximate ages for employees in the given year
    Assumes that they have a birth year filled
    """
    return list(map(lambda x: x.calculate_age(year), employees))
