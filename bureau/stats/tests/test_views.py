from django.test import TestCase
from django.urls import reverse

from medical.tests.factories import AilmentFactory, AilmentTypeFactory
from military.tests.factories import RegimentFactory
from personnel.models import Employee
from personnel.tests.factories import EmployeeFactory
from places.tests.factories import CountryFactory, PlaceFactory, RegionFactory
from stats.views import get_places_with_pks_for_context, get_state_comparison_stats

class DetailedViewTestCase(TestCase):
    """
    Test DetailedView
    """

    def setUp(self):
        self.url = reverse('stats:detailed')
        self.context_keys = ['average_age_in_1865', 'median_age_in_1865','average_age_at_death', 'median_age_at_death',
                    'foreign_born', 'top_birthplaces', 'ailments']

    def test_get_context_data(self):
        """
        Shouldn't cause an error if there's nothing in the database
        """
        # First test it with no data at all
        response = self.client.get(self.url)
        for key in self.context_keys:
            self.assertIn(key, response.context, "'{}' should be in context of DetailedView".format(key))

        # Now test with an Ailment but no Employees
        AilmentFactory()
        response = self.client.get(self.url)
        for key in self.context_keys:
            self.assertIn(key, response.context, "'{}' should be in context of DetailedView".format(key))

        # Test with a birthplace to see if it appears in top birthplaces
        place = PlaceFactory()
        EmployeeFactory(place_of_birth=place)
        response = self.client.get(self.url)
        self.assertIn(str(place), response.context, "Top place of birth should be in context of DetailedView")

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'stats/detailed.html')


class GeneralViewTestCase(TestCase):
    """
    Test GeneralView
    """

    def setUp(self):
        self.url = reverse('stats:general')

    def test_get_context_data(self):
        EmployeeFactory(colored=True)
        EmployeeFactory(confederate_veteran=True)
        EmployeeFactory(gender=Employee.Gender.FEMALE)
        EmployeeFactory(vrc=True)
        EmployeeFactory(vrc=True)

        response = self.client.get(self.url)
        self.assertEqual(response.context['employee_count'], 5,
                         'employee_count should be in context')

        self.assertEqual(response.context['colored_count'], 1,
                         'colored_count should be in context')
        self.assertEqual(response.context['confederate_count'], 1,
                         'confederate_count should be in context')
        self.assertEqual(response.context['female_count'], 1,
                         'female_count should be in context')
        self.assertEqual(response.context['vrc_count'], 2,
                         'vrc_count should be in context')

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'stats/general.html')


class GetPlacesWithPksForContextTestCase(TestCase):
    """
    get_places_with_pks_for_context() should take list of place names (country or region) and counts,
    get the corresponding Place, and return list of names, pks, and counts
    """

    def test_get_places_with_pks_for_context(self):
        PlaceFactory(country=CountryFactory(name='Canada'))
        new_york = PlaceFactory(region=RegionFactory(name='New York', country=CountryFactory(name='United States')))
        spain = PlaceFactory(country=CountryFactory(name='Spain'))

        input = [('New York', 'United States', 43), (None, 'Spain', 5)]
        expected_output = [('New York', new_york.pk, 43), ('Spain', spain.pk, 5)]

        # Compare the lists as sets because order isn't important
        self.assertSetEqual(set(get_places_with_pks_for_context(input)), set(expected_output),
                            'get_places_with_pks_for_context() should return names, pks, and counts for places from input')


class GetStateComparisonStatsTestCase(TestCase):
    """
    get_state_comparison_stats(x) should return stats on the top x Bureau states for various measures
    """

    def setUp(self):
        self.kentucky = RegionFactory(name='Kentucky', bureau_operations=True)
        self.mississippi = RegionFactory(name='Mississippi', bureau_operations=True)
        self.texas = RegionFactory(name='Texas', bureau_operations=True)

    def get_state_stats_for_key(self, stats, key):
        """
        Given all the stats, return the ones for a given key by extracting them from a list with the format
        [(key, state queryset), (key, state queryset)]
        """

        label, states = [item for item in stats if key in item][0]

        # Most have been annotated with a 'value' field, but a least one has a 'total' instead
        return [(state.name, state.value or state.total) for state in states]

    def test_get_state_comparison_stats_employee_count(self):
        """
        'Employee count' should contain states with the top x employee counts
        """

        key = 'Employee count'

        # 1 employee in Kentucky
        for i in range(1):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.kentucky)

        # 2 employees in Texas
        for i in range(2):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.texas)

        # 3 employees in Mississippi
        for i in range(3):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.mississippi)

        expected_output = [('Mississippi', 3), ('Texas', 2)]

        stats = get_state_comparison_stats(number=2)
        top_states = self.get_state_stats_for_key(stats, key)

        self.assertListEqual(top_states, expected_output,
                             "'{}' should contain states with the top x employee counts".format(key))

    def test_get_state_comparison_stats_vrc(self):
        """
        '% VRC employees' should contain states with the top x percentage of VRC member employees
        """

        key = '% VRC employees'

        # 1 VRC employee in Texas, and 3 non-VRC
        for i in range(1):
            employee = EmployeeFactory(vrc=True)
            employee.bureau_states.add(self.texas)
        for i in range(3):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.texas)

        # 1 VRC employee in Kentucky, and 1 non-VRC
        for i in range(1):
            employee = EmployeeFactory(vrc=True)
            employee.bureau_states.add(self.kentucky)
        for i in range(1):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.kentucky)

        # 3 VRC employees in Mississippi
        for i in range(3):
            employee = EmployeeFactory(vrc=True)
            employee.bureau_states.add(self.mississippi)

        expected_output = [('Mississippi', 100), ('Kentucky', 50)]

        stats = get_state_comparison_stats(number=2)
        top_states = self.get_state_stats_for_key(stats, key)

        self.assertListEqual(top_states, expected_output,
                             "'{}' should contain states with the top x % VRC member employees".format(key))

    def test_get_state_comparison_stats_usct(self):
        """
        '% USCT employees' should contain states with the top x percentage of USCT member employees
        """

        key = '% USCT employees'

        usct_regiment = RegimentFactory(usct=True)
        non_usct_regiment = RegimentFactory()

        # 0 USCT employees in Kentucky, and 2 non-USCT
        for i in range(2):
            employee = EmployeeFactory()
            employee.regiments.add(non_usct_regiment)
            employee.bureau_states.add(self.kentucky)

        # 1 USCT employee in Texas, and 3 non-USCT
        for i in range(1):
            employee = EmployeeFactory()
            employee.regiments.add(usct_regiment)
            employee.bureau_states.add(self.texas)
        for i in range(3):
            employee = EmployeeFactory()
            employee.regiments.add(non_usct_regiment)
            employee.bureau_states.add(self.texas)

        # 3 USCT employees in Mississippi, and 1 non-USCT
        for i in range(3):
            employee = EmployeeFactory()
            employee.regiments.add(usct_regiment)
            employee.bureau_states.add(self.mississippi)
        for i in range(1):
            employee = EmployeeFactory()
            employee.regiments.add(non_usct_regiment)
            employee.bureau_states.add(self.mississippi)

        expected_output = [('Mississippi', 75), ('Texas', 25)]

        stats = get_state_comparison_stats(number=2)
        top_states = self.get_state_stats_for_key(stats, key)

        self.assertListEqual(top_states, expected_output,
                             "'{}' should contain states with the top x % USCT member employees".format(key))

    def test_get_state_comparison_stats_foreign_born(self):
        """
        '% Foreign-born employees' should contain states with the top x percentage of foreign-born employees,
        out of the employees whose birthplace is known
        """

        key = '% Foreign-born employees'

        us = CountryFactory(code2='US')
        germany = CountryFactory(name='Germany')

        # Mississippi: 0 employees born in Germany, 3 in US
        for i in range(3):
            employee = EmployeeFactory(place_of_birth=PlaceFactory(country=us))
            employee.bureau_states.add(self.mississippi)

        # Texas: 2 employees born in Germany, 2 in US
        for i in range(2):
            employee = EmployeeFactory(place_of_birth=PlaceFactory(country=germany))
            employee.bureau_states.add(self.texas)
        for i in range(2):
            employee = EmployeeFactory(place_of_birth=PlaceFactory(country=us))
            employee.bureau_states.add(self.texas)

        # Kentucky: 3 employees born in Germany, 1 employee in US, 3 unknown
        for i in range(3):
            employee = EmployeeFactory(place_of_birth=PlaceFactory(country=germany))
            employee.bureau_states.add(self.kentucky)
        for i in range(1):
            employee = EmployeeFactory(place_of_birth=PlaceFactory(country=us))
            employee.bureau_states.add(self.kentucky)
        for i in range(3):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.kentucky)

        expected_output = [('Kentucky', 75), ('Texas', 50)]

        stats = get_state_comparison_stats(number=2)
        top_states = self.get_state_stats_for_key(stats, key)

        self.assertListEqual(top_states, expected_output,
                             "'{}' should contain states with the top x % foreign-born employees".format(key))

    def test_get_state_comparison_stats_born_there(self):
        """
        '% Employees born there' should contain states with the top x percentage of employees born in that state,
        out of the employees whose birthplace is known
        """

        key = '% Employees born there'

        place_kentucky = PlaceFactory(region=self.kentucky)
        place_texas = PlaceFactory(region=self.texas)

        # Mississippi: 0 employees born in Mississippi, 3 born elsewhere
        for i in range(3):
            employee = EmployeeFactory(place_of_birth=PlaceFactory())
            employee.bureau_states.add(self.mississippi)

        # Texas: 2 employees born in Texas, 2 born elsewhere
        for i in range(2):
            employee = EmployeeFactory(place_of_birth=place_texas)
            employee.bureau_states.add(self.texas)
        for i in range(2):
            employee = EmployeeFactory(place_of_birth=PlaceFactory())
            employee.bureau_states.add(self.texas)

        # Kentucky: 3 employees born in Kentucky, 1 employee elsewhere, 3 unknown
        for i in range(3):
            employee = EmployeeFactory(place_of_birth=place_kentucky)
            employee.bureau_states.add(self.kentucky)
        for i in range(1):
            employee = EmployeeFactory(place_of_birth=PlaceFactory())
            employee.bureau_states.add(self.kentucky)
        for i in range(3):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.kentucky)

        expected_output = [('Kentucky', 75), ('Texas', 50)]

        stats = get_state_comparison_stats(number=2)
        top_states = self.get_state_stats_for_key(stats, key)

        self.assertListEqual(top_states, expected_output,
                             "'{}' should contain states with the top x % employees born there".format(key))

    def test_get_state_comparison_stats_female(self):
        """
        '% Female employees' should contain states with the top x percentage of female employees
        """

        key = '% Female employees'

        # 1 female employee in Texas, and 3 male
        for i in range(1):
            employee = EmployeeFactory(gender=Employee.Gender.FEMALE)
            employee.bureau_states.add(self.texas)
        for i in range(3):
            employee = EmployeeFactory(gender=Employee.Gender.MALE)
            employee.bureau_states.add(self.texas)

        # 1 female employee in Kentucky, and 1 male
        for i in range(1):
            employee = EmployeeFactory(gender=Employee.Gender.FEMALE)
            employee.bureau_states.add(self.kentucky)
        for i in range(1):
            employee = EmployeeFactory(gender=Employee.Gender.MALE)
            employee.bureau_states.add(self.kentucky)

        # 3 female employees in Mississippi
        for i in range(3):
            employee = EmployeeFactory(gender=Employee.Gender.FEMALE)
            employee.bureau_states.add(self.mississippi)

        expected_output = [('Mississippi', 100), ('Kentucky', 50)]

        stats = get_state_comparison_stats(number=2)
        top_states = self.get_state_stats_for_key(stats, key)

        self.assertListEqual(top_states, expected_output,
                             "'{}' should contain states with the top x % female employees".format(key))

    def test_get_state_comparison_stats_died_during_assignment(self):
        """
        '% Employees who died during assignment' should contain states with the top x percentage of employees who died
        during an assignment
        """

        key = '% Employees who died during assignment'

        # Kentucky: 0 employees who died during an assignment, and 2 who didn't
        for i in range(2):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.kentucky)

        # Mississippi: 1 employee who died during an assignment, and 1 who didn't
        for i in range(1):
            employee = EmployeeFactory(died_during_assignment=True)
            employee.bureau_states.add(self.mississippi)
        for i in range(1):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.mississippi)

        # Texas: 9 employees who died during an assignment, and 1 who didn't
        for i in range(9):
            employee = EmployeeFactory(died_during_assignment=True)
            employee.bureau_states.add(self.texas)
        for i in range(1):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.texas)

        expected_output = [('Texas', 90), ('Mississippi', 50)]

        stats = get_state_comparison_stats(number=2)
        top_states = self.get_state_stats_for_key(stats, key)

        self.assertListEqual(top_states, expected_output,
                             "'{}' should contain states with the top x % of employees who died during assignment".format(key))

    def test_get_state_comparison_stats_identified_as_colored(self):
        """
        '% Employees identified as "colored"' should contain states with the top x percentage of employees identified
        as "colored"
        """

        key = '% Employees identified as "colored"'

        # 1 "colored" employee in Texas, and 3 not
        for i in range(1):
            employee = EmployeeFactory(colored=True)
            employee.bureau_states.add(self.texas)
        for i in range(3):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.texas)

        # 1 "colored" employee in Kentucky, and 1 not
        for i in range(1):
            employee = EmployeeFactory(colored=True)
            employee.bureau_states.add(self.kentucky)
        for i in range(1):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.kentucky)

        # 3 "colored" employees in Mississippi
        for i in range(3):
            employee = EmployeeFactory(colored=True)
            employee.bureau_states.add(self.mississippi)

        expected_output = [('Mississippi', 100), ('Kentucky', 50)]

        stats = get_state_comparison_stats(number=2)
        top_states = self.get_state_stats_for_key(stats, key)

        self.assertListEqual(top_states, expected_output,
                             "'{}' should contain states with the top x % of employees identified as 'colored'".format(key))

    def test_get_state_comparison_stats_former_slave(self):
        """
        'Former slave employees' should contain states with the top x number of former slave employees
        """

        key = 'Former slave employees'

        # 0 former slave employees in Kentucky, and 2 not
        for i in range(2):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.kentucky)

        # 1 former slave employee in Texas, and 3 not
        for i in range(1):
            employee = EmployeeFactory(former_slave=True)
            employee.bureau_states.add(self.texas)
        for i in range(3):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.texas)

        # 3 former slave employees in Mississippi, and 1 not
        for i in range(3):
            employee = EmployeeFactory(former_slave=True)
            employee.bureau_states.add(self.mississippi)
        for i in range(1):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.mississippi)

        expected_output = [('Mississippi', 3), ('Texas', 1)]

        stats = get_state_comparison_stats(number=2)
        top_states = self.get_state_stats_for_key(stats, key)

        self.assertListEqual(top_states, expected_output,
                             "'{}' should contain states with the top x number of former slave employees".format(key))

    def test_get_state_comparison_stats_former_slaveholder(self):
        """
        '% Former slaveholder employees' should contain states with the top x percentage of employees who were former
        slaveholders
        """

        key = '% Former slaveholder employees'

        # Kentucky: 0 former slaveholder employees, and 2 who weren't
        for i in range(2):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.kentucky)

        # Mississippi: 1 former slaveholder employee who died during an assignment, and 1 who wasn't
        for i in range(1):
            employee = EmployeeFactory(slaveholder=True)
            employee.bureau_states.add(self.mississippi)
        for i in range(1):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.mississippi)

        # Texas: 1 former slaveholder employee, and 9 who weren't
        for i in range(1):
            employee = EmployeeFactory(slaveholder=True)
            employee.bureau_states.add(self.texas)
        for i in range(9):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.texas)

        expected_output = [('Mississippi', 50), ('Texas', 10)]

        stats = get_state_comparison_stats(number=2)
        top_states = self.get_state_stats_for_key(stats, key)

        self.assertListEqual(top_states, expected_output,
                             "'{}' should contain states with the top x % of former slaveholder employees".format(key))

    def test_get_state_comparison_stats_confederate(self):
        """
        '% Ex-Confederate employees' should contain states with the top x percentage of employees who were Confederate
        veterans
        """

        key = '% Ex-Confederate employees'

        # 1 ex-Confederate employee in Texas, and 3 not
        for i in range(1):
            employee = EmployeeFactory(confederate_veteran=True)
            employee.bureau_states.add(self.texas)
        for i in range(3):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.texas)

        # 1 ex-Confederate employee in Kentucky, and 1 not
        for i in range(1):
            employee = EmployeeFactory(confederate_veteran=True)
            employee.bureau_states.add(self.kentucky)
        for i in range(1):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.kentucky)

        # 3 ex-Confederate employees in Mississippi
        for i in range(3):
            employee = EmployeeFactory(confederate_veteran=True)
            employee.bureau_states.add(self.mississippi)

        expected_output = [('Mississippi', 100), ('Kentucky', 50)]

        stats = get_state_comparison_stats(number=2)
        top_states = self.get_state_stats_for_key(stats, key)

        self.assertListEqual(top_states, expected_output,
                             "'{}' should contain states with the top x % of Confederate veteran employees".format(key))

    def test_get_state_comparison_stats_penmanship_contest(self):
        """
        'Left-hand penmanship contest entrants' should contain states with the top x number of employees who entered the
        left-hand penmanship contest
        """

        key = 'Left-hand penmanship contest entrants'

        # Mississippi: 0 employees who entered the contest, 3 who didn't
        for i in range(3):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.mississippi)

        # Texas: 2 employees who entered the contest, 2 who didn't
        for i in range(2):
            employee = EmployeeFactory(penmanship_contest=True)
            employee.bureau_states.add(self.texas)
        for i in range(2):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.texas)

        # Kentucky: 3 employees who entered the contest, 1 who didn't
        for i in range(3):
            employee = EmployeeFactory(penmanship_contest=True)
            employee.bureau_states.add(self.kentucky)
        for i in range(1):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.kentucky)

        expected_output = [('Kentucky', 3), ('Texas', 2)]

        stats = get_state_comparison_stats(number=2)
        top_states = self.get_state_stats_for_key(stats, key)

        self.assertListEqual(top_states, expected_output,
                             "'{}' should contain states with the top x number of employees who entered contest".format(key))

    def test_get_state_comparison_stats_ailments(self):
        """
        Breakdowns by ailment/ailment type should contain states with the top % of employees who had various ailments
        """

        # AilmentType and Ailment breakdown per AilmentType should be in returned stats if present
        ailment_type_headache = AilmentTypeFactory(name='Headache')
        ailment_migraine_headache = AilmentFactory(name='Migraine Headache', type=ailment_type_headache)
        ailment_tension_headache = AilmentFactory(name='Tension Headache', type=ailment_type_headache)
        ailment_type_sprain_or_bruise = AilmentTypeFactory(name='Sprain or Bruise')
        ailment_sprain = AilmentFactory(name='Sprain', type=ailment_type_sprain_or_bruise)

        # Texas: 2 with sprain and 2 with nothing
        for i in range(2):
            employee = EmployeeFactory()
            employee.ailments.add(ailment_sprain)
            employee.bureau_states.add(self.texas)
        for i in range(2):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.texas)

        # Kentucky: 1 with migraine headache, 1 with sprain, 1 with tension headache, and 1 with nothing
        for i in range(1):
            employee = EmployeeFactory()
            employee.ailments.add(ailment_migraine_headache)
            employee.bureau_states.add(self.kentucky)
        for i in range(1):
            employee = EmployeeFactory()
            employee.ailments.add(ailment_sprain)
            employee.bureau_states.add(self.kentucky)
        for i in range(1):
            employee = EmployeeFactory()
            employee.ailments.add(ailment_tension_headache)
            employee.bureau_states.add(self.kentucky)
        for i in range(1):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.kentucky)

        # Mississippi: 2 with migraine headache, 2 with tension headache
        for i in range(2):
            employee = EmployeeFactory()
            employee.ailments.add(ailment_migraine_headache)
            employee.bureau_states.add(self.mississippi)
        for i in range(2):
            employee = EmployeeFactory()
            employee.ailments.add(ailment_tension_headache)
            employee.bureau_states.add(self.mississippi)

        stats = get_state_comparison_stats(number=2)

        # With ailment types, ailments should be grouped together
        key = '% With Headache'
        expected_output = [('Mississippi', 100), ('Kentucky', 50)]
        top_states = self.get_state_stats_for_key(stats, key)
        self.assertListEqual(top_states, expected_output,
                             "'{}' should contain states with the top x % of employees with headache".format(key))

        key = '% With Sprain or Bruise'
        expected_output = [('Texas', 50), ('Kentucky', 25)]
        top_states = self.get_state_stats_for_key(stats, key)
        self.assertListEqual(top_states, expected_output,
                             "'{}' should contain states with the top x % of employees with sprain or bruise".format(key))

        # Ailments should be treated individually
        key = '% With Migraine Headache'
        expected_output = [('Mississippi', 50), ('Kentucky', 25)]
        top_states = self.get_state_stats_for_key(stats, key)
        self.assertListEqual(top_states, expected_output,
                             "'{}' should contain states with the top x % of employees with migraine headache".format(key))

        key = '% With Tension Headache'
        expected_output = [('Mississippi', 50), ('Kentucky', 25)]
        top_states = self.get_state_stats_for_key(stats, key)
        self.assertListEqual(top_states, expected_output,
                             "'{}' should contain states with the top x % of employees with tension headache".format(key))

        # There should be no breakdown for sprain, because it's the only ailment of that type
        key = '% With Sprain'
        self.assertEqual(len([item for item in stats if key in item]), 0,
                         "There should be no breakdown for an ailment if it's the only one of its type")


class StateComparisonViewTestCase(TestCase):
    """
    Test StateComparison
    """

    def setUp(self):
        self.url = reverse('stats:state_comparison')

    def test_get_context_data(self):
        response = self.client.get(self.url)
        self.assertIn('stats', response.context,
                        "StateComparisonView's context should contain 'stats'")

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'stats/state_comparison.html')
