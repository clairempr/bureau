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
        ages_vrc = get_ages_in_year(employees_with_dob.filter(vrc=True), 1865)
        ages_non_vrc = get_ages_in_year(employees_with_dob.filter(vrc=False), 1865)
        ages_usct = get_ages_in_year(employees_with_dob.intersection(Employee.objects.usct()), 1865)
        ages_everyone = ages_vrc + ages_non_vrc

        average_age_in_1865 = {'vrc': get_mean(ages_vrc),
                      'non_vrc': get_mean(ages_non_vrc),
                      'usct': get_mean(ages_usct),
                      'everyone': get_mean(ages_everyone)}

        median_age_in_1865 = {'vrc': get_median(ages_vrc),
                      'non_vrc': get_median(ages_non_vrc),
                      'usct': get_median(ages_usct),
                      'everyone': get_median(ages_everyone)}

        # Age at time of death
        ages_vrc_at_death = get_ages_at_death(employees_with_dob_and_dod.filter(vrc=True))
        ages_non_vrc_at_death = get_ages_at_death(employees_with_dob_and_dod.filter(vrc=False))
        ages_usct_at_death = get_ages_at_death(employees_with_dob_and_dod.intersection(Employee.objects.usct()))
        ages_everyone_at_death = ages_vrc_at_death + ages_non_vrc_at_death

        average_age_at_death ={'vrc': get_mean(ages_vrc_at_death),
                      'non_vrc': get_mean(ages_non_vrc_at_death),
                      'usct': get_mean(ages_usct_at_death),
                      'everyone': get_mean(ages_everyone_at_death)}

        median_age_at_death = {'vrc': get_median(ages_vrc_at_death),
                      'non_vrc': get_median(ages_non_vrc_at_death),
                      'usct': get_median(ages_usct_at_death),
                      'everyone': get_median(ages_everyone_at_death)}

        # Foreign born
        foreign_born_vrc = Employee.objects.foreign_born(vrc=True).count()
        foreign_born_non_vrc = Employee.objects.foreign_born(vrc=False).count()
        foreign_born_usct = Employee.objects.foreign_born().intersection(Employee.objects.usct()).count()
        foreign_born = {'vrc': get_percent(foreign_born_vrc, Employee.objects.birthplace_known(vrc=True).count()),
                        'non_vrc': get_percent(
                            foreign_born_non_vrc, Employee.objects.birthplace_known(vrc=False).count()),
                        'usct': get_percent(foreign_born_usct, Employee.objects.birthplace_known().intersection(
                            Employee.objects.usct()).count()),
                        'everyone': get_percent(
                            (foreign_born_vrc + foreign_born_non_vrc), Employee.objects.birthplace_known().count())}

        # Top places where employees were born
        top_birthplaces = Place.objects.values('region__name', 'country__name').annotate(
            num_employees=Count('employees_born_in')).order_by('-num_employees')[:25]

        # Ailments
        ailments = []
        for ailment in Ailment.objects.all():
            ages_at_death = get_ages_at_death(employees_with_dob_and_dod.filter(ailments=ailment))
            ailments.append(
                {'name': ailment.name,
                 'vrc': get_percent(Employee.objects.vrc(ailments=ailment).count(), Employee.objects.vrc().count()),
                 'non_vrc': get_percent(Employee.objects.non_vrc(
                     ailments=ailment).count(), Employee.objects.non_vrc().count()),
                 'usct': get_percent(Employee.objects.usct(ailments=ailment).count(), Employee.objects.usct().count()),
                 'everyone': get_percent(Employee.objects.filter(ailments=ailment).count(), employee_count),
                 'average_age_at_death': get_mean(ages_at_death),
                 'median_age_at_death': get_median(ages_at_death)})

        ages_at_death = get_ages_at_death(employees_with_dob_and_dod.filter(ailments=None))
        ailments.append({'name': 'None',
                         'vrc': get_percent(Employee.objects.vrc(ailments=None).count(),
                                            Employee.objects.vrc().count()),
                         'non_vrc': get_percent(Employee.objects.non_vrc(ailments=None).count(),
                                                Employee.objects.non_vrc().count()),
                         'usct': get_percent(Employee.objects.usct(ailments=None).count(),
                                             Employee.objects.usct().count()),
                         'everyone': get_percent(Employee.objects.filter(ailments=None).count(), employee_count),
                         'average_age_at_death': get_mean(ages_at_death),
                         'median_age_at_death': get_median(ages_at_death)})

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


def get_ages_at_death(employees):
    """
    Calculate approximate age at death for employees
    Assumes that they have a birth year and death year filled
    """
    return list(map(lambda x: x.age_at_death(), employees))

def get_ages_in_year(employees, year):
    """
    Calculate approximate ages for employees in the given year
    Assumes that they have a birth year filled
    """
    return list(map(lambda x: x.calculate_age(year), employees))

def get_mean(data):
    """
    Return the mean of the data, or 0 if there is no data
    """
    return statistics.mean(data) if data else 0

def get_median(data):
    """
    Return the median of the data, or 0 if there is no data
    """
    return statistics.median(data) if data else 0

def get_percent(part, total):
    """
    Return the percentage that part is of total and multiply by 100
    If total is 0, return 0
    """
    return (part / total) * 100 if part and total else 0

