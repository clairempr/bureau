from unittest.mock import patch

from django.test import TestCase

from personnel.models import EmployeeManager
from personnel.views import EmployeesBornResidedDiedInPlaceView
from places.tests.factories import PlaceFactory

class EmployeesBornResidedDiedInPlaceViewTestCase(TestCase):
    """
    Test EmployeesBornResidedDiedInPlaceView
    """

    def setUp(self):
        self.place = PlaceFactory()
        self.view = EmployeesBornResidedDiedInPlaceView()

    def test_get_place(self):
        """
        If place is in kwargs and it's the pk of a Place, then Place should be returned,
        otherwise None should be returned
        """

        self.view.kwargs = {}
        self.assertIsNone(self.view.get_place(),
                          "EmployeesBornResidedDiedInPlaceView.get_place() should return None if 'place' not in kwargs")

        self.view.kwargs = {'place': 1}
        self.assertIsNone(self.view.get_place(),
                          "EmployeesBornResidedDiedInPlaceView.get_place() should return None if Place obj not found")

        self.view.kwargs = {'place': self.place.pk}
        self.assertEqual(self.view.get_place(), self.place,
                          "EmployeesBornResidedDiedInPlaceView.get_place() should return Place with pk 'place'")

    @patch.object(EmployeesBornResidedDiedInPlaceView, 'get_place', autospec=True)
    @patch.object(EmployeeManager, 'born_in_place', return_value='employees_born_in_place',autospec=True)
    @patch.object(EmployeeManager, 'resided_in_place', return_value='employees_resided_in_place', autospec=True)
    @patch.object(EmployeeManager, 'died_in_place', return_value='employees_died_in_place', autospec=True)
    def test_get_context_data(self, mock_died_in_place, mock_resided_in_place, mock_born_in_place, mock_get_place):
        """
        get_context_data() should fill 'place' with specified place and fill 'employees_born_in_place',
        'employees_resided_in_place', and 'employees_died_in_place'
        """

        context_keys = ['employees_born_in_place', 'employees_resided_in_place', 'employees_died_in_place']

        # If 'place' not found, context['place'] should be empty and employees_* shouldn't be in context at all
        mock_get_place.return_value = None
        context_data = self.view.get_context_data()
        self.assertIsNone(context_data['place'],
                "If place is None, EmployeesBornResidedDiedInPlaceView context['place'] should be None")
        for key in context_keys:
            self.assertNotIn(key, context_data,
                "'{}' shouldn't be in context of EmployeesBornResidedDiedInPlaceView if place is None".format(key))

        # If 'place' is found, it should go in context['place']
        mock_get_place.return_value = self.place
        context_data = self.view.get_context_data()
        self.assertEqual(context_data['place'], self.place,
                "If place is found, it should go in EmployeesBornResidedDiedInPlaceView context['place']")

        # If place is set, other context keys should be filled using EmployeeManager.born_in_place(),
        # resided_in_place(), and died_in_place()
        self.assertEqual(context_data['employees_born_in_place'], mock_born_in_place.return_value,
            "'employees_born_in_place' in context of EmployeesBornResidedDiedInPlaceView should be set to born_in_place()")
        self.assertEqual(context_data['employees_resided_in_place'], mock_resided_in_place.return_value,
            "'employees_resided_in_place' in context of EmployeesBornResidedDiedInPlaceView should be set to resided_in_place()")
        self.assertEqual(context_data['employees_died_in_place'], mock_died_in_place.return_value,
            "'employees_died_in_place' in context of EmployeesBornResidedDiedInPlaceView should be set to died_in_place()")
