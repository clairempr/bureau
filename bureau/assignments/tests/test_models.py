from partial_date import PartialDate
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from assignments.models import Assignment
from assignments.tests.factories import AssignmentFactory, PositionFactory
from places.tests.factories import CityFactory, CountyFactory, PlaceFactory, RegionFactory


class AssignmentTestCase(TestCase):
    """
    Test Assignment model
    """

    def setUp(self):
        self.position1 = PositionFactory(title='Pig Keeper')
        self.position2 = PositionFactory(title='Assistant Pig Keeper')
        self.place1 = PlaceFactory(city=CityFactory())
        self.place2 = PlaceFactory(city=CityFactory())
        self.start_date = PartialDate('1866')
        self.end_date = PartialDate('1867')
        description = 'Position1 and Position2, Place1 and Place2, 1866 - 1867'
        self.assignment = AssignmentFactory(description=description, start_date=self.start_date, end_date=self.end_date)
        self.assignment.positions.add(self.position1, self.position2)
        self.assignment.places.add(self.place1, self.place2)

    def test_str(self):
        """
        Assignment.__str__() should return a string containing info about positions, places, and dates of Assignment
        In cases where one of those things can't be accessed without causing an exception
        (deleting an inline Assignment in Employee admin, for example), __str__() should return Assignment.description
        """

        self.assertTrue(self.assignment.position_list() in str(self.assignment),
                        'Assignment.__str__ should contain Assignment.position_list()')
        self.assertTrue(self.assignment.place_list() in str(self.assignment),
                        'Assignment.__str__ should contain Assignment.place_list()')
        self.assertTrue(self.assignment.dates() in str(self.assignment),
                        'Assignment.__str__ should contain Assignment.dates()')

        # If accessing position_list() causes an exception, __str__() should return description
        with patch.object(Assignment, 'position_list', side_effect=RecursionError(), autospec=True):
            self.assertEqual(str(self.assignment), self.assignment.description,
                'Assignment.__str__ should be equal to Assignment.description if position_list() causes exception')

        # If accessing place_list() causes an exception, __str__() should return description
        with patch.object(Assignment, 'place_list', side_effect=RecursionError(), autospec=True):
            self.assertEqual(str(self.assignment), self.assignment.description,
                'Assignment.__str__ should be equal to Assignment.description if place_list() causes exception')

    def test_dates(self):
        """
        Assignment.dates() should return start and end dates, or just start or end,
        or settings.DEFAULT_EMPTY_FIELD_STRING if no dates are set
        """

        # Assignment with both start and end dates
        assignment = AssignmentFactory(start_date=self.start_date, end_date=self.end_date)
        self.assertTrue(str(self.start_date) in assignment.dates(),
                        'Assignment.start_date should be in Assignment.dates() if Assignment has start and end dates')
        self.assertTrue(str(self.end_date) in assignment.dates(),
                        'Assignment.end_date should be in Assignment.dates() if Assignment has start and end dates')

        # Assignment with just start date
        assignment = AssignmentFactory(start_date=self.start_date)
        self.assertTrue(str(self.start_date) in assignment.dates(),
                        'Assignment.start_date should be in Assignment.dates() if Assignment has only start date')

        # Assignment with just end date
        assignment = AssignmentFactory(end_date=self.end_date)
        self.assertTrue(str(self.end_date) in assignment.dates(),
                        'Assignment.end_date should be in Assignment.dates() if Assignment has only end date')

        # Assignment with no dates
        assignment = AssignmentFactory()
        self.assertEqual(assignment.dates(), settings.DEFAULT_EMPTY_FIELD_STRING,
                        "Assignment.dates() should return '{}' if Assignment has no dates".format(
                            settings.DEFAULT_EMPTY_FIELD_STRING))

    def test_place_list(self):
        """
        Assignment.place_list() should return ' and '-separated list of place names (without country),
        or settings.DEFAULT_EMPTY_FIELD_STRING if no places are set
        """

        # Assignment with places
        for place in [self.place1, self.place2]:
            self.assertTrue(place.name_without_country() in self.assignment.place_list(),
                            'Place.name_without_country() should be in Assignment.place_list()')

        # Assignment with no places
        assignment = AssignmentFactory()
        self.assertEqual(assignment.place_list(), settings.DEFAULT_EMPTY_FIELD_STRING,
                         "Assignment.place_list() should return '{}' if Assignment has no places".format(
                             settings.DEFAULT_EMPTY_FIELD_STRING))

    def test_position_list(self):
        """
        Assignment.position_list() should return ' and '-separated list of positions,
        or settings.DEFAULT_EMPTY_FIELD_STRING if no positions are set
        """

        # Assignment with positions
        for position in [self.position1, self.position2]:
            self.assertTrue(str(position) in self.assignment.position_list(),
                            'Position should be in Assignment.position_list()')

        # Assignment with no positions
        assignment = AssignmentFactory()
        self.assertEqual(assignment.position_list(), settings.DEFAULT_EMPTY_FIELD_STRING,
                         "Assignment.position_list() should return '{}' if Assignment has no positions".format(
                             settings.DEFAULT_EMPTY_FIELD_STRING))


class AssignmentManagerTestCase(TestCase):
    """
    Test AssignmentManager
    """

    def test_during_year(self):
        """
        during_year(year) should return assignments that took place (at least partially) sometime that year
        """

        # Assignment not in year at all shouldn't in queryset
        self.assertNotIn(AssignmentFactory(start_date=PartialDate('1865')), Assignment.objects.during_year(1866),
                         "Assignment not in year shouldn't be in Assignment.objects.during_year()")

        # Assignment that starts in year and has no end date should be in queryset
        self.assertIn(AssignmentFactory(start_date=PartialDate('1866')),
                      Assignment.objects.during_year(1866),
                      "Assignment that starts in year and has no end date should be in Assignment.objects.during_year()")

        # Assignment that starts and ends in year should be in queryset
        self.assertIn(AssignmentFactory(start_date=PartialDate('1866-01'), end_date=PartialDate('1866-03')),
                      Assignment.objects.during_year(1866),
                      "Assignment that starts and ends in year should be in Assignment.objects.during_year()")

        # Assignment that starts before and ends after year should be in queryset
        self.assertIn(AssignmentFactory(start_date=PartialDate('1865'), end_date=PartialDate('1867')),
                      Assignment.objects.during_year(1866),
                      "Assignment that starts before and ends after year should be in Assignment.objects.during_year()")

        # Assignment that starts before and ends in year should be in queryset
        self.assertIn(AssignmentFactory(start_date=PartialDate('1865'), end_date=PartialDate('1866')),
                      Assignment.objects.during_year(1866),
                      "Assignment that starts before and ends in year should be in Assignment.objects.during_year()")

        # Assignment that starts in and ends after year should be in queryset
        self.assertIn(AssignmentFactory(start_date=PartialDate('1866'), end_date=PartialDate('1867')),
                      Assignment.objects.during_year(1866),
                      "Assignment that starts in and ends after year should be in Assignment.objects.during_year()")

    def test_in_place(self):
        """
        in_place() should return assignments in a particular place, according to how specific the place is
        """

        # Set up places
        alabama = PlaceFactory(city=None, county=None, region=RegionFactory(name='alabama'))
        bacon_level = PlaceFactory(city=CityFactory(name='Bacon Level', region=alabama.region, country=alabama.country),
                                   county=None)
        randolph_county = PlaceFactory(city=None, county=CountyFactory(name='Randolph', state=alabama.region,
                                                                       country=alabama.country))

        # Set up assignments
        assignment_in_alabama = AssignmentFactory()
        assignment_in_alabama.places.add(alabama)
        assignment_in_bacon_level = AssignmentFactory()
        assignment_in_bacon_level.places.add(bacon_level)
        assignment_in_randolph_county = AssignmentFactory()
        assignment_in_randolph_county.places.add(randolph_county)

        # If exact is True, only assignments in that exact place should be returned
        self.assertIn(assignment_in_alabama, Assignment.objects.in_place(alabama, exact=True),
                      'Assignment.objects.in_place(exact=True) for state should return assignments in that state')
        for assignment in [assignment_in_bacon_level, assignment_in_randolph_county]:
            self.assertNotIn(assignment, Assignment.objects.in_place(alabama, exact=True),
                    "Assignment.objects.in_place(exact=True) for state shouldn't return assignments in city or county")
        self.assertIn(assignment_in_bacon_level, Assignment.objects.in_place(bacon_level, exact=True),
                      'Assignment.objects.in_place(exact=True) for city should return assignments in that city')
        for assignment in [assignment_in_alabama, assignment_in_randolph_county]:
            self.assertNotIn(assignment, Assignment.objects.in_place(bacon_level, exact=True),
                        'Assignment.objects.in_place(exact=True) for city should only return assignments in city')
        self.assertIn(assignment_in_randolph_county, Assignment.objects.in_place(randolph_county, exact=True),
                      'Assignment.objects.in_place(exact=True) for county should return assignments in that county')
        for assignment in [assignment_in_alabama, assignment_in_bacon_level]:
            self.assertNotIn(assignment, Assignment.objects.in_place(randolph_county, exact=True),
                        'Assignment.objects.in_place(exact=True) for county should only return assignments in county')

        # If exact is False, assignments in that place and places in that place should be returned
        for assignment in [assignment_in_alabama, assignment_in_bacon_level, assignment_in_randolph_county]:
            self.assertIn(assignment, Assignment.objects.in_place(alabama, exact=False),
                          'Assignment.objects.in_place(exact=False) for state should return all assignments in state')
        self.assertIn(assignment_in_bacon_level, Assignment.objects.in_place(bacon_level, exact=False),
                      'Assignment.objects.in_place(exact=False) for city should return assignments in that city')
        for assignment in [assignment_in_alabama, assignment_in_randolph_county]:
            self.assertNotIn(assignment, Assignment.objects.in_place(bacon_level, exact=False),
                        'Assignment.objects.in_place(exact=False) for city should only return assignments in city')
        self.assertIn(assignment_in_randolph_county, Assignment.objects.in_place(randolph_county, exact=False),
                      'Assignment.objects.in_place(exact=False) for county should return assignments in that county')
        for assignment in [assignment_in_alabama, assignment_in_bacon_level]:
            self.assertNotIn(assignment, Assignment.objects.in_place(randolph_county, exact=False),
                        'Assignment.objects.in_place(exact=False) for county should only return assignments in county')


class PositionTestCase(TestCase):
    """
    Test Position model
    """

    def test_str(self):
        """
        __str__ should return Position.title
        """

        title = 'Assistant to the Assistant Subassistant Commissioner'
        position = PositionFactory(title=title)
        self.assertEqual(str(position), title,
                        "Position.__str__ should be equal to Position.title")
