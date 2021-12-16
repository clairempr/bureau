from partial_date import PartialDate

from django.test import TestCase

from assignments.models import Assignment
from assignments.tests.factories import AssignmentFactory, PositionFactory
from places.tests.factories import CityFactory, CountyFactory, PlaceFactory, RegionFactory


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
