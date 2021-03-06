import statistics

from django.db.models import Case, CharField, Count, F, FloatField, Q, Value, When
from django.db.models.functions import Cast
from django.views.generic.base import TemplateView

from medical.models import Ailment, AilmentType
from personnel.models import Employee
from places.models import Place, Region
from places.settings import GERMANY_COUNTRY_NAMES

class GeneralView(TemplateView):
    template_name = 'stats/general.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee_count'] = Employee.objects.count()
        context['colored_count'] = Employee.objects.filter(colored=True).count()
        context['confederate_count'] = Employee.objects.filter(confederate_veteran=True).count()
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
        # Group Germany, Prussia, Bavaria, and Saxony, etc. together, because of inconsistencies in reporting of German
        # places in the sources
        # Group Virginia and West Virginia together, because it was all Virginia when they were born
        top_birthplaces = Place.objects.annotate(
            annotated_country=Case(
                When(country__name__in=GERMANY_COUNTRY_NAMES, then=Value('Germany')),
                default=F('country__name'), output_field=CharField(),
            ),
            annotated_region=Case(
                When(region__name__in=['Virginia', 'West Virginia'], then=Value('Virginia')),
                default=F('region__name'), output_field=CharField(),
            ),
        ).values_list('annotated_region', 'annotated_country').annotate(
            num_employees=Count('employees_born_in')).order_by('-num_employees')[:25]

        top_deathplaces = Place.objects.annotate(
            annotated_country=Case(
                When(country__name__in=GERMANY_COUNTRY_NAMES, then=Value('Germany')),
                default=F('country__name'), output_field=CharField(),
            ),
        ).values_list('region__name', 'annotated_country').annotate(
            num_employees=Count('employees_died_in')).order_by('-num_employees')[:25]

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
        context['top_deathplaces'] = top_deathplaces
        context['ailments'] = ailments
        return context


detailed_view = DetailedView.as_view()


class StateComparisonView(TemplateView):
    template_name = 'stats/state_comparison.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stats = []

        total_employees = Region.objects.bureau_state().annotate(
            total=Cast(Count('employee_employed'), FloatField()))

        # Top employee count
        top_total = total_employees.annotate(value=F('total')).exclude(value=0).order_by('-value')[:5]
        stats.append(('Employee count', top_total))

        # Top % VRC employees
        top_vrc_percent = total_employees.annotate(
            value=Cast(Count('employee_employed', filter=Q(employee_employed__vrc=True)), FloatField()) / F(
                'total') * 100).exclude(value=0).order_by('-value')[:5]
        stats.append(('% VRC employees', top_vrc_percent))

        # Top % USCT employees
        top_usct_percent = total_employees.annotate(
            value=Cast(Count('employee_employed', filter=Q(employee_employed__in=Employee.objects.usct())),
                       FloatField()) / F('total') * 100).exclude(value=0).order_by('-value')[:5]
        stats.append(('% USCT employees', top_usct_percent))

        if Employee.objects.birthplace_known().exists():
            # Top % foreign-born employees
            top_foreign_born_percent = total_employees.annotate(
                value=Cast(Count('employee_employed', filter=Q(employee_employed__in=Employee.objects.foreign_born())),
                           FloatField()) / Cast(Count('employee_employed',
                                                      filter=Q(employee_employed__in=Employee.objects.birthplace_known())),
                           FloatField()) * 100).exclude(value=0).order_by('-value')[:5]
            stats.append(('% Foreign-born employees', top_foreign_born_percent))

            # Top % employees born in that state
            top_born_in_state_percent = total_employees.annotate(
                value=Cast(Count('employee_employed', filter=Q(employee_employed__place_of_birth__region__id=F('id'))),
                           FloatField()) / Cast(Count('employee_employed',
                                                      filter=Q(employee_employed__in=Employee.objects.birthplace_known())),
                                                FloatField()) * 100).exclude(value=0).order_by('-value')[:5]
            stats.append(('% Employees born there', top_born_in_state_percent))

        # Top % female employees
        top_female_percent = total_employees.annotate(
            value=Cast(Count('employee_employed', filter=Q(employee_employed__gender=Employee.FEMALE)),
                       FloatField()) / F('total') * 100).exclude(value=0).order_by('-value')[:5]
        stats.append(('% Female employees', top_female_percent))

        # Top % employees who died during assignment
        top_died_during_assignment_percent = total_employees.annotate(
            value=Cast(Count('employee_employed', filter=Q(employee_employed__died_during_assignment=True)),
                       FloatField()) / F('total') * 100).exclude(value=0).order_by('-value')[:5]
        stats.append(('% Employees who died during assignment', top_died_during_assignment_percent))

        # Top % employees identified as "colored"
        top_colored_percent = total_employees.annotate(
            value=Cast(Count('employee_employed', filter=Q(employee_employed__colored=True)),
                       FloatField()) / F('total') * 100).exclude(value=0).order_by('-value')[:5]
        stats.append(('% Employees identified as "colored"', top_colored_percent))

        # Top # former slave employees
        top_former_slave_percent = total_employees.annotate(
            value=Count('employee_employed', filter=Q(employee_employed__former_slave=True))).exclude(
            value=0).order_by('-value')[:5]
        stats.append(('Former slave employees', top_former_slave_percent))

        # Top % former slaveholder employees
        top_slaveholder_percent = total_employees.annotate(
            value=Cast(Count('employee_employed', filter=Q(employee_employed__slaveholder=True)),
                       FloatField()) / F('total') * 100).exclude(value=0).order_by('-value')[:5]
        stats.append(('% Former slaveholder employees', top_slaveholder_percent))

        # Top % ex-Confederate employees
        top_confederate_percent = total_employees.annotate(
            value=Cast(Count('employee_employed', filter=Q(employee_employed__confederate_veteran=True)),
                       FloatField()) / F('total') * 100).exclude(value=0).order_by('-value')[:5]
        stats.append(('% Ex-Confederate employees', top_confederate_percent))

        # Top # left-hand penmanship contest entrants
        top_penmanship_contest = total_employees.annotate(
            value=Count('employee_employed', filter=Q(employee_employed__penmanship_contest=True))).exclude(
            value=0).order_by('-value')[:5]
        stats.append(('Left-hand penmanship contest entrants', top_penmanship_contest))

        # Breakdown per AilmentType
        for ailment_type in AilmentType.objects.all():
            top_ailment_type_percent = total_employees.annotate(
                value=Cast(Count('employee_employed', filter=Q(employee_employed__ailments__type=ailment_type)),
                       FloatField()) / F('total') * 100).exclude(value=0).order_by('-value')[:5]
            stats.append(('% With {}'.format(ailment_type), top_ailment_type_percent))

            # Breakdown per Ailment, if more than one for the type
            if ailment_type.ailments.count() > 1:
                for ailment in ailment_type.ailments.all():
                    top_ailment_percent = total_employees.annotate(
                        value=Cast(Count('employee_employed', filter=Q(employee_employed__ailments=ailment)),
                                   FloatField()) / F('total') * 100).exclude(value=0).order_by('-value')[:5]
                    stats.append(('% With {}'.format(ailment), top_ailment_percent))

        context['stats'] = stats
        return context


state_comparison_view = StateComparisonView.as_view()


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

