from partial_date import PartialDate

from django.test import TestCase

from assignments.models import Assignment
from assignments.tests.factories import AssignmentFactory, PositionFactory


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
