from unittest.mock import patch

from django.test import RequestFactory, TestCase
from django.urls import reverse

from medical.tests.factories import AilmentFactory, AilmentTypeFactory
from personnel.models import Employee, EmployeeManager
from personnel.tests.factories import EmployeeFactory
from personnel.views import EmployeeListView, EmployeesBornResidedDiedInPlaceView, EmployeesWithAilmentListView
from places.tests.factories import BureauStateFactory, CityFactory, CountryFactory, PlaceFactory, RegionFactory


class EmployeeListViewTestCase(TestCase):
    """
    Test EmployeeListView
    """

    def setUp(self):
        self.url = 'personnel:employee_list'
        self.rebecca_crumpler = EmployeeFactory(first_name='Rebecca Lee', last_name='Crumpler', gender=Employee.Gender.FEMALE)
        self.william_van_duyn = EmployeeFactory(first_name='William B.', last_name='Van Duyn', gender=Employee.Gender.MALE)
        self.bureau_state1 = BureauStateFactory()
        self.bureau_state2 = BureauStateFactory()
        self.boolean_keys = ['vrc', 'union_veteran', 'confederate_veteran', 'colored', 'died_during_assignment',
                             'former_slave', 'slaveholder']
        self.search_keys = ['first_name', 'last_name', 'gender', 'place_of_birth', 'place_of_death']

    def test_get_context_data(self):
        """
        context should contain any GET parameters (aside from "Clear"), if "clear" isn't True
        """

        request = RequestFactory().get('/')
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        context = view.get_context_data()

        # If GET parameter wasn't supplied for search criteria, they should be empty in context
        for key in self.search_keys:
            self.assertEqual(context[key], '', f"If GET parameter {key} not supplied, it should be empty in context")

        # If GET parameter was supplied for search criteria, they should be filled in context
        search_text = 'search text'
        for key in self.search_keys:
            response = self.client.get(reverse(self.url), {key: search_text})
            self.assertEqual(response.context[key], search_text,
                             "If {key} was supplied, it should be in context of EmployeeListView")
        for key in self.boolean_keys:
            response = self.client.get(reverse(self.url), {key: 'on'})
            self.assertEqual(response.context[key], key,
                             "If {key} was supplied, it should be in context of EmployeeListView")

        # Some things should always be in context
        response = self.client.get(reverse(self.url))
        for key in ['bureau_states', 'ailments']:
            self.assertIn(key, response.context, "{key} should always be in context of EmployeeListView")

    def test_get_context_clear(self):
        """
        context should containn't any GET parameters if "clear" is True
        """

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

        # If GET parameter "clear" was true, search criteria shouldn't be filled in context
        for key in self.search_keys + self.boolean_keys:
            response = self.client.get(reverse(self.url), {'clear': 'true', key: 'value'})
            self.assertNotIn(key, response.context,
                             "If clear was True, no search criteria should be in context of EmployeeListView")

        # bureau_states is list of tuples: (state, selected)
        arkansas = BureauStateFactory(name='Arkansas')
        bureau_states = [str(arkansas.pk)]
        response = self.client.get(reverse(self.url), {'clear': 'true', 'bureau_states': bureau_states})
        for state, selected in response.context['bureau_states']:
            self.assertFalse(selected,
                             'If clear was True supplied, no bureau_states should be selected in context')
        # ailments is list of tuples: (ailment, selected)
        gunshot_wound = AilmentFactory(name='Gunshot wound')
        ailments = [str(gunshot_wound.pk)]
        response = self.client.get(reverse(self.url), {'clear': 'true', 'ailments': ailments})
        for ailment, selected in response.context['ailments']:
            self.assertFalse(selected,
                             'If clear was True supplied, no ailments should be selected in context')

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

    def test_get_queryset_by_place_of_birth(self):
        germany = PlaceFactory(country=CountryFactory(name='Germany'))
        bavaria = PlaceFactory(country=CountryFactory(name='Bavaria'))
        virginia = PlaceFactory(region=RegionFactory(name='Virginia'))
        west_virginia = PlaceFactory(region=RegionFactory(name='West Virginia'))
        philadelphia = PlaceFactory(city=CityFactory(name='Philadelphia'), region=RegionFactory(name='Pennsylvania'))
        employee_born_in_germany = EmployeeFactory(place_of_birth=germany)
        employee_born_in_bavaria = EmployeeFactory(place_of_birth=bavaria)
        employee_born_in_virginia = EmployeeFactory(place_of_birth=virginia)
        employee_born_in_west_virginia = EmployeeFactory(place_of_birth=west_virginia)
        employee_born_in_philadelphia = EmployeeFactory(place_of_birth=philadelphia)

        # If country is Germany, other places like Bavaria should be included
        # otherwise it should be just that country
        request = RequestFactory().get('/', {'place_of_birth': 'Germany'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {employee_born_in_germany, employee_born_in_bavaria},
            'If Germany specified as place_of_birth, EmployeeListView should return employees born in Germany and Bavaria')
        request = RequestFactory().get('/', {'place_of_birth': 'Bavaria'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {employee_born_in_bavaria},
            'If country specified as place_of_birth, EmployeeListView should return employees born in that country')

        # State: search for "Virginia" will automatically include West Virginia, which is what we want
        request = RequestFactory().get('/', {'place_of_birth': 'Virginia'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {employee_born_in_virginia, employee_born_in_west_virginia},
            'If state place_of_birth specified, EmployeeListView should return employees with search text in state name')
        request = RequestFactory().get('/', {'place_of_birth': 'West Virginia'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {employee_born_in_west_virginia},
            'If state place_of_birth specified, EmployeeListView should return employees with search text in state name')

        # City
        request = RequestFactory().get('/', {'place_of_birth': 'Philadelphia'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {employee_born_in_philadelphia},
            'If city place_of_birth specified, EmployeeListView should return employees with search text in city name')

    def test_get_queryset_by_place_of_death(self):
        germany = PlaceFactory(country=CountryFactory(name='Germany'))
        bavaria = PlaceFactory(country=CountryFactory(name='Bavaria'))
        virginia = PlaceFactory(region=RegionFactory(name='Virginia'))
        west_virginia = PlaceFactory(region=RegionFactory(name='West Virginia'))
        philadelphia = PlaceFactory(city=CityFactory(name='Philadelphia'), region=RegionFactory(name='Pennsylvania'))
        employee_died_in_germany = EmployeeFactory(place_of_death=germany)
        employee_died_in_bavaria = EmployeeFactory(place_of_death=bavaria)
        employee_died_in_virginia = EmployeeFactory(place_of_death=virginia)
        employee_died_in_west_virginia = EmployeeFactory(place_of_death=west_virginia)
        employee_died_in_philadelphia = EmployeeFactory(place_of_death=philadelphia)

        # If country is Germany, other places like Bavaria should be included
        # otherwise it should be just that country
        request = RequestFactory().get('/', {'place_of_death': 'Germany'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {employee_died_in_germany, employee_died_in_bavaria},
            'If Germany specified as place_of_death, EmployeeListView should return employees who died in Germany and Bavaria')
        request = RequestFactory().get('/', {'place_of_death': 'Bavaria'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {employee_died_in_bavaria},
            'If country specified as place_of_death, EmployeeListView should return employees who died in that country')

        # State: search for "Virginia" should not include West Virginia
        request = RequestFactory().get('/', {'place_of_death': 'Virginia'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {employee_died_in_virginia},
            'If Virginia specified as place_of_death, EmployeeListView should return employees who died in Virginia only')
        request = RequestFactory().get('/', {'place_of_death': 'West Virginia'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {employee_died_in_west_virginia},
            'If state place_of_death specified, EmployeeListView should return employees with search text in state name')

        # City
        request = RequestFactory().get('/', {'place_of_death': 'Philadelphia'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {employee_died_in_philadelphia},
            'If city place_of_death specified, EmployeeListView should return employees with search text in city name')

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

    def test_get_queryset_by_veteran_status(self):
        union_employee = EmployeeFactory(union_veteran=True)
        confederate_employee = EmployeeFactory(confederate_veteran=True)
        non_veteran_employee = EmployeeFactory()

        request = RequestFactory().get('/')
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        for employee in [union_employee, confederate_employee, non_veteran_employee]:
            self.assertIn(employee, queryset,
                    'If veteran status not specified, EmployeeListView should return veteran and non-veteran employees')

        request = RequestFactory().get('/', {'union_veteran': 'union_veteran'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertIn(union_employee, queryset,
                      'If union_veteran specified, EmployeeListView should return Union veteran employees')
        for employee in [confederate_employee, non_veteran_employee]:
            self.assertNotIn(employee, queryset,
                      'If union_veteran specified, EmployeeListView should return only Union veteran employees')

        request = RequestFactory().get('/', {'confederate_veteran': 'confederate_veteran'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertIn(confederate_employee, queryset,
                    'If confederate_veteran specified, EmployeeListView should return Confederate veteran employees')
        for employee in [union_employee, non_veteran_employee]:
            self.assertNotIn(employee, queryset,
                    'If confederate_veteran specified, EmployeeListView should return only Confederate veteran employees')

    def test_get_queryset_by_colored_status(self):
        """
        Test filtering by (self-)identification as "Colored"
        """
        colored_employee = EmployeeFactory(colored=True)
        non_colored_employee = EmployeeFactory(colored=False)

        request = RequestFactory().get('/')
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        for employee in [colored_employee, non_colored_employee]:
            self.assertIn(employee, queryset,
                    'If "Colored" not specified, EmployeeListView should return "Colored" and non-"Colored" employees')

        request = RequestFactory().get('/', {'colored': 'colored'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertIn(colored_employee, queryset,
                      'If "Colored" specified, EmployeeListView should return "Colored" employees')
        self.assertNotIn(non_colored_employee, queryset,
                         'If "Colored" specified, EmployeeListView should return only "Colored" employees')

    def test_get_queryset_by_died_during_assignment_status(self):

        died_during_assignment_employee = EmployeeFactory(died_during_assignment=True)
        non_died_during_assignment_employee = EmployeeFactory(died_during_assignment=False)

        request = RequestFactory().get('/')
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        for employee in [died_during_assignment_employee, non_died_during_assignment_employee]:
            self.assertIn(employee, queryset,
                'If died_during_assignment not specified, EmployeeListView should return employees whether they died during assignment or not')

        request = RequestFactory().get('/', {'died_during_assignment': 'died_during_assignment'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertIn(died_during_assignment_employee, queryset,
            'If died_during_assignment specified, EmployeeListView should return employees who died during assignment')
        self.assertNotIn(non_died_during_assignment_employee, queryset,
            'If died_during_assignment_employee specified, EmployeeListView should return only employees who died during assignment')

    def test_get_queryset_by_former_slave_status(self):
        former_slave_employee = EmployeeFactory(former_slave=True)
        non_former_slave_employee = EmployeeFactory(former_slave=False)

        request = RequestFactory().get('/')
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        for employee in [former_slave_employee, non_former_slave_employee]:
            self.assertIn(employee, queryset,
                'If former_slave not specified, EmployeeListView should return employees whether or not they were a former slave')

        request = RequestFactory().get('/', {'former_slave': 'former_slave'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertIn(former_slave_employee, queryset,
                      'If former_slave specified, EmployeeListView should return former slave employees')
        self.assertNotIn(non_former_slave_employee, queryset,
                         'If former_slave specified, EmployeeListView should return only former slave employees')

    def test_get_queryset_by_slaveholder_status(self):
        slaveholder_employee = EmployeeFactory(slaveholder=True)
        non_slaveholder_employee = EmployeeFactory(slaveholder=False)

        request = RequestFactory().get('/')
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        for employee in [slaveholder_employee, non_slaveholder_employee]:
            self.assertIn(employee, queryset,
                'If slaveholder not specified, EmployeeListView should return employees whether or not they were a slaveholder')

        request = RequestFactory().get('/', {'slaveholder': 'slaveholder'})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertIn(slaveholder_employee, queryset,
                      'If slaveholder specified, EmployeeListView should return slaveholder employees')
        self.assertNotIn(non_slaveholder_employee, queryset,
                         'If slaveholder specified, EmployeeListView should return only slaveholder employees')

    def test_get_queryset_by_ailments(self):
        ailment1 = AilmentFactory()
        ailment2 = AilmentFactory()
        employee_with_ailment_1 = EmployeeFactory()
        employee_with_ailment_1.ailments.add(ailment1)
        employee_with_ailments_1_and_2 = EmployeeFactory()
        employee_with_ailments_1_and_2.ailments.add(ailment1, ailment2)

        request = RequestFactory().get('/', {'ailments': [ailment1.pk, ailment2.pk]})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {employee_with_ailment_1, employee_with_ailments_1_and_2},
                            'If ailments specified, EmployeeListView should return employees with at least one')

        request = RequestFactory().get('/', {'ailments': [ailment2.pk]})
        view = EmployeeListView(kwargs={}, object_list=[], request=request)
        self.assertSetEqual(set(view.get_queryset()), {employee_with_ailments_1_and_2},
                            'If ailments specified, EmployeeListView should return employees with at least one')


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
