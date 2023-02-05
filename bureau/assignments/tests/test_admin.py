from django.contrib.admin import site
from django.test import RequestFactory, TestCase

from assignments.admin import AssignmentAdmin
from assignments.models import Assignment
from assignments.tests.factories import AssignmentFactory, PositionFactory
from places.tests.factories import PlaceFactory


class AssignmentAdminTestCase(TestCase):
    """
    Test AssignmentAdmin
    """

    def test_get_queryset(self):
        """
        get_queryset() should return Assignments with prefetch_related for positions and places
        """
        assignment = AssignmentFactory()
        assignment.places.add(PlaceFactory())
        assignment.positions.add(PositionFactory())

        modeladmin = AssignmentAdmin(Assignment, site)
        request = RequestFactory().get('/')

        # Queryset hasn't yet been retrieved with prefetch_related,
        # so instances should have no _prefetched_objects_cache
        instance = Assignment.objects.first()
        self.assertFalse(hasattr(instance, '_prefetched_objects_cache'))

        qs = modeladmin.get_queryset(request)

        # Queryset has been retrieved with prefetch_related, so instances should have _prefetched_objects_cache
        instance = qs.first()
        self.assertTrue(hasattr(instance, '_prefetched_objects_cache'))
