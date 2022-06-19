from unittest.mock import patch

from django.test import RequestFactory, TestCase
from django.urls import reverse

from medical.tests.factories import AilmentFactory, AilmentTypeFactory
from personnel.models import Employee, EmployeeManager
from personnel.tests.factories import EmployeeFactory
from personnel.views import EmployeeListView, EmployeesBornResidedDiedInPlaceView, EmployeesWithAilmentListView
from places.tests.factories import BureauStateFactory, PlaceFactory


class EmployeeListViewTestCase(TestCase):
    """
    Test EmployeeListView
    """

    def setUp(self):
        self.rebecca_crumpler = EmployeeFactory(first_name='Rebecca Lee', last_name='Crumpler', gender=Employee.Gender.FEMALE)
        self.william_van_duyn = EmployeeFactory(first_name='William B.', last_name='Van Duyn', gender=Employee.Gender.MALE)
        self.bureau_state1 = BureauStateFactory()
        self.bureau_state2 = BureauStateFactory()

    def test_get_context_data(self):
        """
        context should contain any GET parameters (aside from "Clear"), if "clear" isn't True
        """

        url = 'personnel:employee_list'

        request = RequestFactory().get('/')
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        context = view.get_context_data()

        # If GET parameter wasn't supplied for search criteria, they should be empty in context
        for key in ['first_name', 'last_name']:
            self.assertEqual(context[key], '', f"If GET parameter {key} not supplied, it should be empty in context")

        # If GET parameter was supplied for search criteria, they should be filled in context
        search_text = 'this is the name'
        for key in ['first_name', 'last_name', 'gender']:
            response = self.client.get(reverse(url), {key: search_text})
            self.assertEqual(response.context[key], search_text,
                             "If {key} was supplied, it should be in context of EmployeeListView")
        for key in ['vrc', 'union_veteran', 'confederate_veteran']:
            response = self.client.get(reverse(url), {key: 'on'})
            self.assertEqual(response.context[key], key,
                             "If {key} was supplied, it should be in context of EmployeeListView")

        # If GET parameter "clear" was true, search criteria shouldn't be filled in context
        for key in ['first_name', 'last_name']:
            response = self.client.get(reverse(url), {'clear': 'true', key: search_text})
            self.assertNotIn(key, response.context,
                             "If clear was True, no search criteria should be in context of EmployeeListView")

        # Some things should always be in context
        response = self.client.get(reverse(url))
        for key in ['bureau_states']:
            self.assertIn(key, response.context, "{key} should always be in context of EmployeeListView")

    def test_get_queryset_default(self):
        EmployeeFactory()

        request = RequestFactory().get('/')
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertQuerysetEqual(view.get_queryset(), Employee.objects.all())

    def test_get_queryset_clear(self):
        EmployeeFactory()

        # If "clear" is True, search criteria have been cleared and all employees need to be returned
        request = RequestFactory().get('/', {'clear': 'true'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertQuerysetEqual(view.get_queryset(), Employee.objects.all())

    def test_get_queryset_by_gender(self):
        request = RequestFactory().get('/')
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {self.rebecca_crumpler, self.william_van_duyn},
                    'If no gender specified, EmployeeListView should return employees of any gender')

        request = RequestFactory().get('/', {'gender': 'Female'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {self.rebecca_crumpler},
                    'If gender specified, EmployeeListView should return employees of that gender')

        request = RequestFactory().get('/', {'gender': 'Male'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {self.william_van_duyn},
                    'If gender specified, EmployeeListView should return employees of that gender')

    def test_get_queryset_by_name(self):
        for text in ['Rebecca', 'Lee', 'Rebecca Lee']:
            request = RequestFactory().get('/', {'first_name': text})
            view = EmployeeListView(kwargs={}, object_list=[], request=request)
            self.assertSetEqual(set(view.get_queryset()), {self.rebecca_crumpler},
                    'If first_name specified, EmployeeListView should return employees with search text in first_name')

        for text in ['Van', 'Duyn', 'Van Duyn']:
            request = RequestFactory().get('/', {'last_name': text})
            view = EmployeeListView(kwargs={}, object_list=[], request=request)
            self.assertSetEqual(set(view.get_queryset()), {self.william_van_duyn},
                    'If last_name specified, EmployeeListView should return employees with search text in last_name')

    def test_get_queryset_by_bureau_states(self):
        employee_in_state_1 = EmployeeFactory()
        employee_in_state_1.bureau_states.add(self.bureau_state1)
        employee_in_states_1_and_2 = EmployeeFactory()
        employee_in_states_1_and_2.bureau_states.add(self.bureau_state1, self.bureau_state2)

        request = RequestFactory().get('/', {'bureau_states': [self.bureau_state1.pk, self.bureau_state2.pk]})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {employee_in_state_1, employee_in_states_1_and_2},
                    'If bureau_states specified, EmployeeListView should return employees who worked in at least one')

        request = RequestFactory().get('/', {'bureau_states': [self.bureau_state2.pk]})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {employee_in_states_1_and_2},
                    'If bureau_states specified, EmployeeListView should return employees who worked in at least one')

    def test_get_queryset_by_vrc_status(self):
        vrc_employee = EmployeeFactory(vrc=True)
        non_vrc_employee = EmployeeFactory(vrc=False)

        request = RequestFactory().get('/')
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        for employee in [vrc_employee, non_vrc_employee]:
            self.assertIn(employee, queryset,
                          'If VRC not specified, EmployeeListView should return VRC and non-VRC employees')

        request = RequestFactory().get('/', {'vrc': 'vrc'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertIn(vrc_employee, queryset,
                      'If VRC specified, EmployeeListView should return VRC employees')
        self.assertNotIn(non_vrc_employee, queryset,
                      'If VRC specified, EmployeeListView should return only VRC employees')


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
