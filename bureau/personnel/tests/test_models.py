from partial_date import PartialDate

from django.test import TestCase

from assignments.tests.factories import AssignmentFactory, PositionFactory
from military.tests.factories import RegimentFactory
from places.tests.factories import CityFactory, CountryFactory, CountyFactory, PlaceFactory, RegionFactory

from personnel.models import Employee
from personnel.tests.factories import EmployeeFactory


class EmployeeManagerTestCase(TestCase):
    """
    Test EmployeeManager
    """

    def test_birthplace_known(self):
        """
        Should return employees with place_of_birth filled
        """

        self.assertIn(EmployeeFactory(place_of_birth=PlaceFactory()), Employee.objects.birthplace_known(),
                      "Employee with place_of_birth filled should be in Employee.objects.birthplace_known()")
        self.assertNotIn(EmployeeFactory(place_of_birth=None), Employee.objects.birthplace_known(),
                         "Employee with place_of_birth empty shouldn't be in Employee.objects.birthplace_known()")

    def test_employed_during_year_ended_before_year(self):
        """
        Should return employees with assignments during a given year
        """

        # Employee with assignment that ended before year shouldn't be returned
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1865-08', end_date='1865-10', employee=employee)
        self.assertNotIn(employee, Employee.objects.employed_during_year(1866))
        # Check empty end date
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1865-08', employee=employee)
        self.assertNotIn(employee, Employee.objects.employed_during_year(1866))
        # Check start and end dates just year
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1864', end_date='1865', employee=employee)
        self.assertNotIn(employee, Employee.objects.employed_during_year(1866))
        # Check start date just year and empty end date
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1865', employee=employee)
        self.assertNotIn(employee, Employee.objects.employed_during_year(1866))


    def test_employed_during_year_started_before_and_ended_after(self):
        """
        Should return employees with assignments during a given year
        """

        # Employee with assignment that started before year and ended after year should be returned
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1865-08', end_date='1867-10', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))
        # Check start and end dates just year
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1865', end_date='1867', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))


    def test_employed_during_year_started_that_year_and_into_next(self):
        """
        Should return employees with assignments during a given year
        """

        # Employee with assignment that started that year and continued into next year should be returned
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1866-08', end_date='1867-10', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))
        # Check start and end dates just year
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1866', end_date='1867', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))


    def test_employed_during_year_entirely_in_year(self):
        """
        Should return employees with assignments during a given year
        """

        # Employee with assignment entirely in year should be returned
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1866-08', end_date='1866-10', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))
        # Check start date and no end date
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1866-02', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))
        # Check start date just year and no end date
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1866', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))


    def test_employed_during_year_started_year_before_and_into_year(self):
        """
        Should return employees with assignments during a given year
        """

        # Employee with assignment that started year before and continued into that year should be returned
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1865-08', end_date='1866-10', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))
        # Check start and end dates just year
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1865', end_date='1866', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))


    def test_employed_during_year_started_after_year(self):
        """
        Should return employees with assignments during a given year
        """


        # Employee with assignment that started after year shouldn't be returned
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1867-08', end_date='1867-10', employee=employee)
        self.assertNotIn(employee, Employee.objects.employed_during_year(1866))
        # Check empty end date
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1867-08', employee=employee)
        self.assertNotIn(employee, Employee.objects.employed_during_year(1866))
        # Check start and end dates just year
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1867', end_date='1868', employee=employee)
        self.assertNotIn(employee, Employee.objects.employed_during_year(1866))
        # Check start date just year and empty end date
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1867', employee=employee)
        self.assertNotIn(employee, Employee.objects.employed_during_year(1866))


    def test_foreign_born(self):
        """
        Should return employees with place_of_birth filled and country code not 'US'
        """
        self.assertNotIn(EmployeeFactory(place_of_birth=None), Employee.objects.foreign_born(),
                         "Employee with place_of_birth empty shouldn't be in Employee.objects.foreign_born()")
        self.assertNotIn(
            EmployeeFactory(place_of_birth=PlaceFactory(country=CountryFactory(code2='US'))),
            Employee.objects.foreign_born(),
            "Employee with place_of_birth in 'US' shouldn't be in Employee.objects.foreign_born()"
        )
        self.assertIn(
            EmployeeFactory(place_of_birth=PlaceFactory(country=CountryFactory(code2='DE'))),
            Employee.objects.foreign_born(),
            "Employee with place_of_birth in 'DE' should be in Employee.objects.foreign_born()"
        )

    def test_vrc(self):
        """
        Should return employees with vrc=True
        """
        self.assertNotIn(EmployeeFactory(vrc=False), Employee.objects.vrc(),
                         "Employee with vrc=False shouldn't be in Employee.objects.vrc()")
        self.assertIn(EmployeeFactory(vrc=True),
                      Employee.objects.vrc(),
                      "Employee with vrc=True should be in Employee.objects.vrc()")

    def test_non_vrc(self):
        """
        Should return employees with vrc=False
        """
        self.assertNotIn(EmployeeFactory(vrc=True), Employee.objects.non_vrc(),
                         "Employee with vrc=True shouldn't be in Employee.objects.non_vrc()")
        self.assertIn(EmployeeFactory(vrc=False),
                      Employee.objects.non_vrc(),
                      "Employee with vrc=False should be in Employee.objects.non_vrc()")


class EmployeeManagerBornDiedResidedInPlaceTestCase(TestCase):
    """
    Test EmployeeManager.born_in_place(), died_in_place(), and resided_in_place()
    """

    # pylint: disable=too-many-instance-attributes

    def setUp(self):
        # Set up places in Germany and Prussia
        self.germany = PlaceFactory(city=None, county=None, region=None, country=CountryFactory(name='Germany'))
        self.hanover = PlaceFactory(
            city=CityFactory(name='Hanover', country=self.germany.country), county=None, region=None
        )
        self.prussia = PlaceFactory(city=None, county=None, region=None, country=CountryFactory(name='Prussia'))
        self.cologne = PlaceFactory(
            city=CityFactory(name='Cologne', country=self.prussia.country), county=None, region=None
        )

        # Set up places in Virginia and West Virginia
        us = PlaceFactory(city=None, county=None, region=None, country=CountryFactory(name='United States'))
        self.virginia = PlaceFactory(
            city=None, county=None, region=RegionFactory(name='Virginia', country=us.country)
        )
        self.richmond = PlaceFactory(city=CityFactory(name='Richmond', region=self.virginia.region), county=None)
        self.west_virginia = PlaceFactory(
            city=None, county=None, region=RegionFactory(name='West Virginia', country=us.country)
        )
        self.booger_hole = PlaceFactory(
            city=CityFactory(name='Booger Hole', region=self.west_virginia.region, country=us.country), county=None
        )
        self.clay_county = PlaceFactory(
            city=None, county=CountyFactory(name='Clay', state=self.west_virginia.region, country=us.country)
        )

    def test_born_in_place(self):
        """
        born_in_place() should return employees who were born in a particular place,
        according to how specific the place is

        Prussia should get grouped with Germany and West Virginia should get grouped with Virginia
        """

        # Set up employees born in Germany and Prussia
        employee_born_in_germany = EmployeeFactory(place_of_birth=self.germany)
        employee_born_in_hanover = EmployeeFactory(place_of_birth=self.hanover)
        employee_born_in_prussia = EmployeeFactory(place_of_birth=self.prussia)
        employee_born_in_cologne = EmployeeFactory(place_of_birth=self.cologne)

        # Set up employees born in Virginia and West Virginia
        employee_born_in_virginia = EmployeeFactory(place_of_birth=self.virginia)
        employee_born_in_richmond = EmployeeFactory(place_of_birth=self.richmond)
        employee_born_in_west_virginia = EmployeeFactory(place_of_birth=self.west_virginia)
        employee_born_in_booger_hole = EmployeeFactory(place_of_birth=self.booger_hole)
        employee_born_in_clay_county = EmployeeFactory(place_of_birth=self.clay_county)

        # If it's Germany, then employees born in Prussia and places in Prussia should be included
        self.assertIn(employee_born_in_germany, Employee.objects.born_in_place(place=self.germany),
                      'born_in_place() for a country should include employee born in that country')
        self.assertIn(employee_born_in_prussia, Employee.objects.born_in_place(place=self.germany),
                      'born_in_place() should include employee born in Prussia if place is Germany')
        self.assertIn(employee_born_in_cologne, Employee.objects.born_in_place(place=self.germany),
                      'born_in_place() should include employee born in city in Prussia if place is Germany')

        # If it's Prussia, then it should just be Prussia and places in Prussia
        self.assertIn(employee_born_in_prussia, Employee.objects.born_in_place(place=self.prussia),
                      'born_in_place() for a country should include employee born in that country')
        self.assertIn(employee_born_in_cologne, Employee.objects.born_in_place(place=self.prussia),
                      'born_in_place() should include employee born in city in Prussia if place is Prussia')
        self.assertNotIn(employee_born_in_germany, Employee.objects.born_in_place(place=self.prussia),
                         "born_in_place() shouldn't include employee born in another country (unless place is Germany)")

        # If it's Cologne, Prussia, then it should just be Cologne
        self.assertIn(employee_born_in_cologne, Employee.objects.born_in_place(place=self.cologne),
                      'born_in_place() for a city should include employee born in that city')
        self.assertNotIn(employee_born_in_prussia, Employee.objects.born_in_place(place=self.cologne),
                         "born_in_place() shouldn't include every employee born in Prussia if place is city in Prussia")
        self.assertNotIn(employee_born_in_germany, Employee.objects.born_in_place(place=self.cologne),
                         "born_in_place() shouldn't include employee born in Germany if place is city in Prussia")

        # If it's Hanover, Germany, then it should just be Hanover
        self.assertIn(employee_born_in_hanover, Employee.objects.born_in_place(place=self.hanover),
                      'born_in_place() for a city should include employee born in that city')
        self.assertNotIn(employee_born_in_germany, Employee.objects.born_in_place(place=self.hanover),
                         "born_in_place() shouldn't include every employee born in Germany if place is city in Germany")
        self.assertNotIn(employee_born_in_prussia, Employee.objects.born_in_place(place=self.hanover),
                         "born_in_place() shouldn't include employee born in Prussia if place is city in Germany")

        # If it's Virginia, then employees born in West Virginia and places in West Virginia should be included
        self.assertIn(employee_born_in_virginia, Employee.objects.born_in_place(place=self.virginia),
                      'born_in_place() for a state should include employee born in that state')
        self.assertIn(employee_born_in_west_virginia, Employee.objects.born_in_place(place=self.virginia),
                      'born_in_place() should include employee born in West Virginia if place is Virginia')
        self.assertIn(employee_born_in_booger_hole, Employee.objects.born_in_place(place=self.virginia),
                      'born_in_place() should include employee born in city in West Virginia if place is Virginia')
        self.assertIn(employee_born_in_clay_county, Employee.objects.born_in_place(place=self.virginia),
                      'born_in_place() should include employee born in county in West Virginia if place is Virginia')

        # If it's West Virginia, then it should just be West Virginia and places in West Virginia
        self.assertIn(employee_born_in_west_virginia, Employee.objects.born_in_place(place=self.west_virginia),
                      'born_in_place() for a state should include employee born in that state')
        self.assertIn(
            employee_born_in_booger_hole, Employee.objects.born_in_place(place=self.west_virginia),
            'born_in_place() should include employee born in city in West Virginia if place is West Virginia'
        )
        self.assertIn(
            employee_born_in_clay_county, Employee.objects.born_in_place(place=self.west_virginia),
            'born_in_place() should include employee born in county in West Virginia if place is West Virginia'
        )
        self.assertNotIn(employee_born_in_virginia, Employee.objects.born_in_place(place=self.west_virginia),
                         "born_in_place() shouldn't include employee born in another state (unless place is Virginia)")

        # If it's Booger Hole, West Virginia, then it should just be Booger Hole
        self.assertIn(employee_born_in_booger_hole, Employee.objects.born_in_place(place=self.booger_hole),
                      'born_in_place() for a city should include employee born in that city')
        for employee in [employee_born_in_west_virginia, employee_born_in_clay_county]:
            self.assertNotIn(employee, Employee.objects.born_in_place(place=self.booger_hole),
                             "born_in_place() shouldn't include every employee born in state if place is a city")
        self.assertNotIn(employee_born_in_virginia, Employee.objects.born_in_place(place=self.booger_hole),
                         "born_in_place() shouldn't include employee born in another state if place is a city")

        # If it's Clay County, West Virginia, then it should just be Clay County
        self.assertIn(employee_born_in_clay_county, Employee.objects.born_in_place(place=self.clay_county),
                      'born_in_place() for a county should include employee born in that county')
        for employee in [employee_born_in_west_virginia, employee_born_in_booger_hole]:
            self.assertNotIn(employee, Employee.objects.born_in_place(place=self.clay_county),
                             "born_in_place() shouldn't include every employee born in state if place is a county")
        self.assertNotIn(employee_born_in_virginia, Employee.objects.born_in_place(place=self.clay_county),
                         "born_in_place() shouldn't include employee born in another state if place is a county")

        # If it's Richmond, Virginia, then it should just be Richmond
        self.assertIn(employee_born_in_richmond, Employee.objects.born_in_place(place=self.richmond),
                      'born_in_place() for a city should include employee born in that city')
        self.assertNotIn(employee_born_in_virginia, Employee.objects.born_in_place(place=self.richmond),
                         "born_in_place() shouldn't include every employee born in state if place is a city")
        self.assertNotIn(employee_born_in_west_virginia, Employee.objects.born_in_place(place=self.richmond),
                         "born_in_place() shouldn't include employee born in another state if place is a city")

    def test_died_in_place(self):
        """
        born_in_place() should return employees who were born in a particular place,
        according to how specific the place is

        Prussia should get grouped with Germany
        """

        # Set up employees who died in Germany and Prussia
        employee_died_in_germany = EmployeeFactory(place_of_death=self.germany)
        employee_died_in_hanover = EmployeeFactory(place_of_death=self.hanover)
        employee_died_in_prussia = EmployeeFactory(place_of_death=self.prussia)
        employee_died_in_cologne = EmployeeFactory(place_of_death=self.cologne)

        # Set up employees who died in Virginia and West Virginia
        employee_died_in_virginia = EmployeeFactory(place_of_death=self.virginia)
        employee_died_in_west_virginia = EmployeeFactory(place_of_death=self.west_virginia)
        employee_died_in_booger_hole = EmployeeFactory(place_of_death=self.booger_hole)
        employee_died_in_clay_county = EmployeeFactory(place_of_death=self.clay_county)

        # If it's Germany, then employees who died in Prussia and places in Prussia should be included
        self.assertIn(employee_died_in_germany, Employee.objects.died_in_place(place=self.germany),
                      'died_in_place() for a country should include employee who died in that country')
        self.assertIn(employee_died_in_prussia, Employee.objects.died_in_place(place=self.germany),
                      'died_in_place() should include employee who died in Prussia if place is Germany')
        self.assertIn(employee_died_in_cologne, Employee.objects.died_in_place(place=self.germany),
                      'died_in_place() should include employee who died in city in Prussia if place is Germany')

        # If it's Prussia, then it should just be Prussia and places in Prussia
        self.assertIn(employee_died_in_prussia, Employee.objects.died_in_place(place=self.prussia),
                      'died_in_place() for a country should include employee who died in that country')
        self.assertIn(employee_died_in_cologne, Employee.objects.died_in_place(place=self.prussia),
                      'died_in_place() should include employee who died in city in Prussia if place is Prussia')
        self.assertNotIn(
            employee_died_in_germany, Employee.objects.died_in_place(place=self.prussia),
            "died_in_place() shouldn't include employee who died in another country (unless place is Germany)"
        )

        # If it's Cologne, Prussia, then it should just be Cologne
        self.assertIn(employee_died_in_cologne, Employee.objects.died_in_place(place=self.cologne),
                      'died_in_place() for a city should include employee who died in that city')
        self.assertNotIn(
            employee_died_in_prussia, Employee.objects.died_in_place(place=self.cologne),
            "died_in_place() shouldn't include every employee who died in Prussia if place is city in Prussia"
        )
        self.assertNotIn(employee_died_in_germany, Employee.objects.died_in_place(place=self.cologne),
                         "died_in_place() shouldn't include employee who died in Germany if place is city in Prussia")

        # If it's Hanover, Germany, then it should just be Hanover
        self.assertIn(employee_died_in_hanover, Employee.objects.died_in_place(place=self.hanover),
                      'died_in_place() for a city should include employee who died in that city')
        self.assertNotIn(
            employee_died_in_germany, Employee.objects.died_in_place(place=self.hanover),
            "died_in_place() shouldn't include every employee who died in Germany if place is city in Germany"
        )
        self.assertNotIn(employee_died_in_prussia, Employee.objects.died_in_place(place=self.hanover),
                         "died_in_place() shouldn't include employee who died in Prussia if place is city in Germany")

        # If it's West Virginia, then employees who died in West Virginia and places in West Virginia should be included
        self.assertIn(employee_died_in_west_virginia, Employee.objects.died_in_place(place=self.west_virginia),
                      'died_in_place() for a state should include employee who died in that state')
        self.assertIn(employee_died_in_booger_hole, Employee.objects.died_in_place(place=self.west_virginia),
                      'died_in_place() should include employee who died in city in West Virginia if place is WV')
        self.assertIn(employee_died_in_clay_county, Employee.objects.died_in_place(place=self.west_virginia),
                      'died_in_place() should include employee who died in county in West Virginia if place is WV')
        self.assertNotIn(employee_died_in_virginia, Employee.objects.died_in_place(place=self.west_virginia),
                         "died_in_place() shouldn't include employee who died in another state")

        # If it's Booger Hole, West Virginia, then it should just be Booger Hole
        self.assertIn(employee_died_in_booger_hole, Employee.objects.died_in_place(place=self.booger_hole),
                      'died_in_place() for a city should include employee who died in that city')
        for employee in [employee_died_in_west_virginia, employee_died_in_clay_county]:
            self.assertNotIn(employee, Employee.objects.died_in_place(place=self.booger_hole),
                             "died_in_place() shouldn't include every employee who died in state if place is a city")
        self.assertNotIn(employee_died_in_virginia, Employee.objects.died_in_place(place=self.booger_hole),
                         "died_in_place() shouldn't include employee who died in another state if place is a city")

        # If it's Clay County, West Virginia, then it should just be Clay County
        self.assertIn(employee_died_in_clay_county, Employee.objects.died_in_place(place=self.clay_county),
                      'died_in_place() for a county should include employee who died in that county')
        for employee in [employee_died_in_west_virginia, employee_died_in_booger_hole]:
            self.assertNotIn(employee, Employee.objects.died_in_place(place=self.clay_county),
                             "died_in_place() shouldn't include every employee who died in state if place is a county")
        self.assertNotIn(employee_died_in_virginia, Employee.objects.died_in_place(place=self.clay_county),
                         "died_in_place() shouldn't include employee who died in another state if place is a county")

    def test_resided_in_place(self):
        """
        resided_in_place() should return employees who resided in a particular place,
        according to how specific the place is

        Prussia should get grouped with Germany and West Virginia should get grouped with Virginia
        """

        # Set up employees who resided in Germany and Prussia
        employee_resided_in_germany = EmployeeFactory(place_of_residence=self.germany)
        employee_resided_in_hanover = EmployeeFactory(place_of_residence=self.hanover)
        employee_resided_in_prussia = EmployeeFactory(place_of_residence=self.prussia)
        employee_resided_in_cologne = EmployeeFactory(place_of_residence=self.cologne)

        # Set up employees who resided in Virginia and West Virginia
        employee_resided_in_virginia = EmployeeFactory(place_of_residence=self.virginia)
        employee_resided_in_richmond = EmployeeFactory(place_of_residence=self.richmond)
        employee_resided_in_west_virginia = EmployeeFactory(place_of_residence=self.west_virginia)
        employee_resided_in_booger_hole = EmployeeFactory(place_of_residence=self.booger_hole)
        employee_resided_in_clay_county = EmployeeFactory(place_of_residence=self.clay_county)

        # If it's Germany, then employees who resided in Prussia and places in Prussia should be included
        self.assertIn(employee_resided_in_germany, Employee.objects.resided_in_place(place=self.germany),
                      'resided_in_place() for a country should include employee who resided in that country')
        self.assertIn(employee_resided_in_prussia, Employee.objects.resided_in_place(place=self.germany),
                      'resided_in_place() should include employee who resided in Prussia if place is Germany')
        self.assertIn(employee_resided_in_cologne, Employee.objects.resided_in_place(place=self.germany),
                      'resided_in_place() should include employee who resided in city in Prussia if place is Germany')

        # If it's Prussia, then it should just be Prussia and places in Prussia
        self.assertIn(employee_resided_in_prussia, Employee.objects.resided_in_place(place=self.prussia),
                      'resided_in_place() for a country should include employee who resided in that country')
        self.assertIn(employee_resided_in_cologne, Employee.objects.resided_in_place(place=self.prussia),
                      'resided_in_place() should include employee who resided in city in Prussia if place is Prussia')
        self.assertNotIn(
            employee_resided_in_germany, Employee.objects.resided_in_place(place=self.prussia),
            "resided_in_place() shouldn't include employee who resided in another country (unless place is Germany)"
        )

        # If it's Cologne, Prussia, then it should just be Cologne
        self.assertIn(employee_resided_in_cologne, Employee.objects.resided_in_place(place=self.cologne),
                      'resided_in_place() for a city should include employee who resided in that city')
        self.assertNotIn(
            employee_resided_in_prussia, Employee.objects.resided_in_place(place=self.cologne),
            "resided_in_place() shouldn't include every employee who resided in Prussia if place is city in Prussia"
        )
        self.assertNotIn(
            employee_resided_in_germany, Employee.objects.resided_in_place(place=self.cologne),
            "resided_in_place() shouldn't include employee who resided in Germany if place is city in Prussia"
        )

        # If it's Hanover, Germany, then it should just be Hanover
        self.assertIn(employee_resided_in_hanover, Employee.objects.resided_in_place(place=self.hanover),
                      'resided_in_place() for a city should include employee who resided in that city')
        self.assertNotIn(
            employee_resided_in_germany, Employee.objects.resided_in_place(place=self.hanover),
            "resided_in_place() shouldn't include every employee who resided in Germany if place is city in Germany"
        )
        self.assertNotIn(
            employee_resided_in_prussia, Employee.objects.resided_in_place(place=self.hanover),
            "resided_in_place() shouldn't include employee who resided in Prussia if place is city in Germany"
        )

        # If it's Virginia, then employees who resided in West Virginia and places in West Virginia should be included
        self.assertIn(employee_resided_in_virginia, Employee.objects.resided_in_place(place=self.virginia),
                      'resided_in_place() for a state should include employee who resided in that state')
        self.assertIn(employee_resided_in_west_virginia, Employee.objects.resided_in_place(place=self.virginia),
                      'resided_in_place() should include employee who resided in West Virginia if place is Virginia')
        self.assertIn(
            employee_resided_in_booger_hole, Employee.objects.resided_in_place(place=self.virginia),
            'resided_in_place() should include employee who resided in city in West Virginia if place is Virginia'
        )
        self.assertIn(
            employee_resided_in_clay_county, Employee.objects.resided_in_place(place=self.virginia),
            'resided_in_place() should include employee who resided in county in West Virginia if place is Virginia'
        )

        # If it's West Virginia, then it should just be West Virginia and places in West Virginia
        self.assertIn(employee_resided_in_west_virginia, Employee.objects.resided_in_place(place=self.west_virginia),
                      'resided_in_place() for a state should include employee who resided in that state')
        self.assertIn(
            employee_resided_in_booger_hole, Employee.objects.resided_in_place(place=self.west_virginia),
            'resided_in_place() should include employee who resided in city in West Virginia if place is West Virginia'
        )
        self.assertIn(
            employee_resided_in_clay_county, Employee.objects.resided_in_place(place=self.west_virginia),
            'resided_in_place() should include employee who resided in county in West Virginia if place is WV'
        )
        self.assertNotIn(
            employee_resided_in_virginia, Employee.objects.resided_in_place(place=self.west_virginia),
            "resided_in_place() shouldn't include employee who resided in another state (unless place is Virginia)"
        )

        # If it's Booger Hole, West Virginia, then it should just be Booger Hole
        self.assertIn(employee_resided_in_booger_hole, Employee.objects.resided_in_place(place=self.booger_hole),
                      'resided_in_place() for a city should include employee who resided in that city')
        for employee in [employee_resided_in_west_virginia, employee_resided_in_clay_county]:
            self.assertNotIn(
                employee, Employee.objects.resided_in_place(place=self.booger_hole),
                "resided_in_place() shouldn't include every employee who resided in state if place is a city"
            )
        self.assertNotIn(
            employee_resided_in_virginia, Employee.objects.resided_in_place(place=self.booger_hole),
            "resided_in_place() shouldn't include employee who resided in another state if place is a city"
        )

        # If it's Clay County, West Virginia, then it should just be Clay County
        self.assertIn(employee_resided_in_clay_county, Employee.objects.resided_in_place(place=self.clay_county),
                      'resided_in_place() for a county should include employee who resided in that county')
        for employee in [employee_resided_in_west_virginia, employee_resided_in_booger_hole]:
            self.assertNotIn(
                employee, Employee.objects.resided_in_place(place=self.clay_county),
                "resided_in_place() shouldn't include every employee who resided in state if place is a county"
            )
        self.assertNotIn(
            employee_resided_in_virginia, Employee.objects.resided_in_place(place=self.clay_county),
            "resided_in_place() shouldn't include employee who resided in another state if place is a county"
        )

        # If it's Richmond, Virginia, then it should just be Richmond
        self.assertIn(employee_resided_in_richmond, Employee.objects.resided_in_place(place=self.richmond),
                      'resided_in_place() for a city should include employee who resided in that city')
        self.assertNotIn(employee_resided_in_virginia, Employee.objects.resided_in_place(place=self.richmond),
                         "resided_in_place() shouldn't include every employee resided in state if place is a city")
        self.assertNotIn(
            employee_resided_in_west_virginia, Employee.objects.resided_in_place(place=self.richmond),
            "resided_in_place() shouldn't include employee who resided in another state if place is a city"
        )


class EmployeeTestCase(TestCase):
    """
    Test Employee model
    """

    def test_str(self):
        """
        __str__ should return Employee.last_name, Employee.first_name
        """

        employee = EmployeeFactory()
        self.assertEqual(str(employee), f'{employee.last_name}, {employee.first_name}',
                         "Employee.__str__ should be equal to Employee.last_name, Employee.first_name")

    def test_age_at_death(self):
        """
        Should calculate the difference between death year and birth year, if both are filled
        Otherwise it should return None
        """

        self.assertIsNone(EmployeeFactory().age_at_death(),
                          "age_at_death() should be None for employee with no birth or death date")
        self.assertIsNone(EmployeeFactory(date_of_birth=PartialDate('1840')).age_at_death(),
                          "age_at_death() should be None for employee with no death date")
        self.assertIsNone(EmployeeFactory(date_of_death=PartialDate('1890')).age_at_death(),
                          "age_at_death() should be None for employee with no birth date")
        self.assertEqual(
            EmployeeFactory(date_of_birth=PartialDate('1840'), date_of_death=PartialDate('1890')).age_at_death(), 50,
            "age_at_death() should be death year - birth year"
        )

    def test_assignments_in_order(self):
        """
        assignments_in_order() should return employee's assignments ordered by start_date
        """

        employee = EmployeeFactory()

        assignment_1868 = AssignmentFactory(start_date=PartialDate('1868'), employee=employee)
        assignment_1868.positions.add(PositionFactory(title='Agent'))
        assignment_1865 = AssignmentFactory(start_date=PartialDate('1865'), employee=employee)
        assignment_1865.positions.add(PositionFactory(title='Assistant Superintendent'))
        assignment_1867 = AssignmentFactory(start_date=PartialDate('1867'), employee=employee)
        assignment_1867.positions.add(PositionFactory(title='Subassistant Commissioner'))

        self.assertEqual(list(employee.assignments_in_order()), [assignment_1865, assignment_1867, assignment_1868],
                         'assignments_in_order() should return assignments ordered by start_date')

    def test_calculate_age(self):
        """
        Should calculate year - birth year, if birth date filled
        Otherwise it should return None
        """

        self.assertIsNone(EmployeeFactory().calculate_age(1865),
                          "calculate_age() should be None for employee with no birth date")
        self.assertEqual(EmployeeFactory(date_of_birth=PartialDate('1840')).calculate_age(1865), 25,
                         "calculate_age() should be year - birth year")

    def test_vrc_set_on_save(self):
        """
        If Employee is a member of a VRC unit, 'vrc' should be True
        """

        employee = EmployeeFactory(vrc=False)
        employee.regiments.set([RegimentFactory(vrc=True)])
        employee.save()
        employee.refresh_from_db()
        self.assertTrue(employee.vrc,
                        "Employee in VRC unit should have 'vrc' set to true after saving")
