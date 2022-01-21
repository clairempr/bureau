from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from medical.tests.factories import AilmentFactory, AilmentTypeFactory
from personnel.models import EmployeeManager
from personnel.tests.factories import EmployeeFactory
from personnel.views import EmployeesBornResidedDiedInPlaceView, EmployeesWithAilmentListView
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
        If 'place' is in kwargs and it's the pk of a Place, then Place should be returned,
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


class EmployeesWithAilmentListViewTestCase(TestCase):
    """
    Test EmployeesWithAilmentListView
    """

    def setUp(self):
        self.ailment = AilmentFactory()
        self.ailment_type = AilmentTypeFactory()
        self.view = EmployeesWithAilmentListView()

    def test_get_ailment(self):
        """
        If 'ailment' is in kwargs and it's the pk of an Ailment, then Ailment should be returned,
        otherwise None should be returned
        """

        self.view.kwargs = {}
        self.assertIsNone(self.view.get_ailment(),
                          "EmployeesWithAilmentListView.get_ailment() should return None if 'ailment' not in kwargs")

        self.view.kwargs = {'ailment': 1}
        self.assertIsNone(self.view.get_ailment(),
                          "EmployeesWithAilmentListView.get_ailment() should return None if Ailment obj not found")

        self.view.kwargs = {'ailment': self.ailment.pk}
        self.assertEqual(self.view.get_ailment(), self.ailment,
                          "EmployeesWithAilmentListView.get_ailment() should return Ailment with pk 'ailment'")

    def test_get_ailment_type(self):
        """
        If 'ailment_type' is in kwargs and it's the pk of an AilmentType, then AilmentType should be returned,
        otherwise None should be returned
        """

        self.view.kwargs = {}
        self.assertIsNone(self.view.get_ailment_type(),
                "EmployeesWithAilmentListView.get_ailment_type() should return None if 'ailment_type' not in kwargs")

        self.view.kwargs = {'ailment_type': 1}
        self.assertIsNone(self.view.get_ailment_type(),
                "EmployeesWithAilmentListView.get_ailment_type() should return None if AilmentType obj not found")

        self.view.kwargs = {'ailment_type': self.ailment_type.pk}
        self.assertEqual(self.view.get_ailment_type(), self.ailment_type,
                "EmployeesWithAilmentListView.get_ailment_type() should return AilmentType with pk 'ailment_type'")

    @patch.object(EmployeesWithAilmentListView, 'get_ailment', autospec=True)
    @patch.object(EmployeesWithAilmentListView, 'get_ailment_type', autospec=True)
    def test_get_context_data(self, mock_get_ailment_type, mock_get_ailment):
        """
        get_context_data() should fill 'ailment' with an Ailment if specified,
        otherwise 'ailment_type' should be filled with specified AilmentType
        """

        employees_with_ailment_url = reverse('personnel:employees_with_ailment_list',
                                             kwargs={'ailment': self.ailment.pk})
        employees_with_ailment_type_url = reverse('personnel:employees_with_ailment_type_list',
                                             kwargs={'ailment_type': self.ailment_type.pk})

        # If get_ailment() returns an Ailment, context['ailment'] should be filled
        # and 'ailment_type' shouldn't be in context at all
        mock_get_ailment.return_value = self.ailment
        response = self.client.get(employees_with_ailment_url)
        self.assertEqual(response.context['ailment'], self.ailment,
            "If EmployeesBornResidedDiedInPlaceView.get_ailment() returns an Ailment, it should be in context")

        # If get_ailment() returns an Ailment, context['ailment'] should be filled
        # and 'ailment_type' shouldn't be in context at all
        mock_get_ailment.return_value = None
        mock_get_ailment_type.return_value = self.ailment_type
        response = self.client.get(employees_with_ailment_type_url)
        self.assertEqual(response.context['ailment'], self.ailment_type,
            "If EmployeesBornResidedDiedInPlaceView.get_ailment() returns None, AilmentType should be in context")

    @patch.object(EmployeesWithAilmentListView, 'get_ailment', autospec=True)
    @patch.object(EmployeesWithAilmentListView, 'get_ailment_type', autospec=True)
    def test_get_queryset(self, mock_get_ailment_type, mock_get_ailment):
        """
        get_queryset() should return employees with specified Ailment, if get_ailment() returns something
        otherwise if should return employees with AilmentType from get_ailment_type()
        """

        employee_with_ailment = EmployeeFactory()
        employee_with_ailment.ailments.add(self.ailment)

        employee_with_ailment_type = EmployeeFactory()
        employee_with_ailment_type.ailments.add(AilmentFactory(type=self.ailment_type))

        # If get_ailment() returns an Ailment, get_queryset() should return employees with ailment
        mock_get_ailment.return_value = self.ailment
        queryset = self.view.get_queryset()
        self.assertIn(employee_with_ailment, queryset,
            'EmployeesWithAilmentListView.get_queryset() should return employees with ailment if ailment specified')
        self.assertNotIn(employee_with_ailment_type, queryset,
            "EmployeesWithAilmentListView.get_queryset() shouldn't return employees with ailment type if ailment specified")

        # If get_ailment() returns None and get_ailment_type() returns an AilmentType,
        # get_queryset() should return employees with ailment type
        mock_get_ailment.return_value = None
        mock_get_ailment_type.return_value = self.ailment_type
        queryset = self.view.get_queryset()
        self.assertIn(employee_with_ailment_type, queryset,
            'EmployeesWithAilmentListView.get_queryset() should return employees with ailment type if ailment type specified')
        self.assertNotIn(employee_with_ailment, queryset,
            "EmployeesWithAilmentListView.get_queryset() shouldn't return employees with ailment if ailment type specified")

        # If get_ailment() and get_ailment_type() both return None,
        # get_queryset() should return the view's default queryset (all employees)
        mock_get_ailment.return_value = None
        mock_get_ailment_type.return_value = None
        queryset = self.view.get_queryset()
        for employee in [employee_with_ailment, employee_with_ailment_type]:
            self.assertIn(employee, queryset,
            'EmployeesWithAilmentListView.get_queryset() should return all employees if no ailment or ailment type specified')
