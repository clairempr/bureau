from django.test import RequestFactory, TestCase
from django.urls import reverse

from military.models import Regiment
from military.tests.factories import RegimentFactory
from military.views import ConfederateRegimentListView, RegimentListView, RegularArmyRegimentListView, \
    StateRegimentListView, USCTRegimentListView, VRCRegimentListView
from places.tests.factories import RegionFactory


class RegimentListViewTestCase(TestCase):
    """
    Test RegimentListView
    """

    def setUp(self):
        self.maine_regt = RegimentFactory(name='3rd Maine Infantry', state=RegionFactory())
        self.usct_3rd_regt = RegimentFactory(name='3rd US Colored Heavy Artillery', usct=True, us=True)
        self.usct_113th_regt = RegimentFactory(name='113th US Colored Infantry', usct=True, us=True)
        self.vrc_7th_regt = RegimentFactory(name='7th Regiment, Veteran Reserve Corps', vrc=True)
        self.vrc_24th_regt = RegimentFactory(name='24th Regiment, Veteran Reserve Corps', vrc=True)
        self.confederate_alabama_regt = RegimentFactory(name='48th Alabama Infantry',
                                                        state=RegionFactory(), confederate=True)
        self.confederate_georgia_regt = RegimentFactory(name='2nd Georgia Cavalry',
                                                        state=RegionFactory(), confederate=True)

    def test_get_context_data(self):
        """
        context should contain RegimentListView's regiment_type, set to True
        If GET parameter 'search_text' was supplied, that should also be in context
        """

        url = 'military:regiment_list'

        # context[regiment_type] should be True
        request = RequestFactory().get('/')
        view = RegimentListView(regiment_type='some_regiments', kwargs={}, object_list=[], request=request)
        context = view.get_context_data()
        self.assertTrue(context[view.regiment_type], 'RegimentListView.regiment_type should be True in context')

        # If GET parameter search_text was supplied, that should be in context
        search_text = 'this is the search text'
        response = self.client.get(reverse(url), {'search_text': search_text})
        self.assertEqual(response.context['search_text'], search_text,
                         "If 'search_text' was supplied, it should be in context of RegimentListView")

        # If GET parameter search_text not supplied, context['search_text'] should be empty
        response = self.client.get(reverse(url))
        self.assertEqual(response.context['search_text'], '',
                         "If 'search_text' wasn't supplied, it should be empty in context of RegimentListView")

    def test_get_queryset(self):
        """
        If GET parameter 'search_text' is supplied, get_queryset() should filter the default queryset (all Regiments)
        """

        # If no GET parameter 'search_text' supplied, get_queryset() should return default queryset (all Regiments)
        request = RequestFactory().get('/')
        view = RegimentListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertSetEqual(set(queryset), set(Regiment.objects.all()),
                            msg="RegimentListView.get_queryset() should return all regiments if no search_text")

        # If 'search_text' parameter supplied, get_queryset() should filter the default queryset
        request = RequestFactory().get('/', {'search_text': 'Maine'})
        view = RegimentListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertIn(self.maine_regt, queryset,
                      "RegimentListView.get_queryset() should return regiments whose names contain search_text")
        for regiment in Regiment.objects.exclude(pk=self.maine_regt.pk):
            self.assertNotIn(
                regiment, queryset,
                "RegimentListView.get_queryset() should return only regiments whose names contain search_text"
            )


class ConfederateRegimentListViewTestCase(RegimentListViewTestCase):
    """
    Test ConfederateRegimentListView
    """

    def test_get_queryset(self):
        """
        If GET parameter 'search_text' is supplied, get_queryset() should filter the default queryset
        (all Confederate Regiments)
        """

        # If no GET parameter 'search_text' supplied, get_queryset() should return default queryset
        # (all Confederate Regiments)
        request = RequestFactory().get('/')
        view = ConfederateRegimentListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertSetEqual(
            set(queryset), {self.confederate_alabama_regt, self.confederate_georgia_regt},
            "ConfederateRegimentListView.get_queryset() should return all Confederate regiments if no search_text"
        )

        # If 'search_text' parameter supplied, get_queryset() should filter the default queryset
        request = RequestFactory().get('/', {'search_text': 'Georgia'})
        view = ConfederateRegimentListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertSetEqual(
            set(queryset), {self.confederate_georgia_regt},
            "ConfederateRegimentListView.get_queryset() should return regiments whose names contain search_text"
        )


class RegularArmyRegimentListViewTestCase(RegimentListViewTestCase):
    """
    Test RegularArmyRegimentListView
    """

    def test_get_queryset(self):
        """
        If GET parameter 'search_text' is supplied, get_queryset() should filter the default queryset
        (all Regular Army Regiments)
        """

        regular_33rd_infantry_regt = RegimentFactory(name='33rd US Infantry', us=True)
        regular_4th_artillery_regt = RegimentFactory(name='4th US Artillery', us=True)

        # If no GET parameter 'search_text' supplied, get_queryset() should return default queryset
        # (all Regular Army Regiments)
        request = RequestFactory().get('/')
        view = RegularArmyRegimentListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertSetEqual(
            set(queryset), {regular_4th_artillery_regt, regular_33rd_infantry_regt},
            "RegularArmyRegimentListView.get_queryset() should return all Regular Army regiments if no search_text"
        )

        # If 'search_text' parameter supplied, get_queryset() should filter the default queryset
        request = RequestFactory().get('/', {'search_text': '33rd'})
        view = RegularArmyRegimentListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertSetEqual(
            set(queryset), {regular_33rd_infantry_regt},
            "RegularArmyRegimentListView.get_queryset() should return regiments whose names contain search_text"
        )


class StateRegimentListViewTestCase(RegimentListViewTestCase):
    """
    Test StateRegimentListView
    """

    def test_get_queryset(self):
        """
        If GET parameter 'search_text' is supplied, get_queryset() should filter the default queryset
        (all state Regiments)
        """

        # If no GET parameter 'search_text' supplied, get_queryset() should return default queryset
        # (all state Regiments)
        request = RequestFactory().get('/')
        view = StateRegimentListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertSetEqual(
            set(queryset),
            {self.maine_regt, self.confederate_alabama_regt, self.confederate_georgia_regt},
            "StateRegimentListView.get_queryset() should return all state regiments if no search_text supplied"
        )

        # If 'search_text' parameter supplied, get_queryset() should filter the default queryset
        request = RequestFactory().get('/', {'search_text': 'Georgia'})
        view = StateRegimentListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertSetEqual(
            set(queryset), {self.confederate_georgia_regt},
            "StateRegimentListView.get_queryset() should return regiments whose names contain search_text"
        )


class USCTRegimentListViewTestCase(RegimentListViewTestCase):
    """
    Test USCTRegimentListView
    """

    def test_get_queryset(self):
        """
        If GET parameter 'search_text' is supplied, get_queryset() should filter the default queryset
        (all USCT Regiments)
        """

        # If no GET parameter 'search_text' supplied, get_queryset() should return default queryset
        # (all USCT Regiments)
        request = RequestFactory().get('/')
        view = USCTRegimentListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertSetEqual(
            set(queryset),
            {self.usct_3rd_regt, self.usct_113th_regt},
            "USCTRegimentListView.get_queryset() should return all USCT regiments if no search_text supplied"
        )

        # If 'search_text' parameter supplied, get_queryset() should filter the default queryset
        request = RequestFactory().get('/', {'search_text': '113th'})
        view = USCTRegimentListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertSetEqual(
            set(queryset), {self.usct_113th_regt},
            "USCTRegimentListView.get_queryset() should return USCT regiments whose names contain search_text"
        )


class VRCRegimentListViewTestCase(RegimentListViewTestCase):
    """
    Test VRCRegimentListView
    """

    def test_get_queryset(self):
        """
        If GET parameter 'search_text' is supplied, get_queryset() should filter the default queryset
        (all VRC Regiments)
        """

        # If no GET parameter 'search_text' supplied, get_queryset() should return default queryset
        # (all VRC Regiments)
        request = RequestFactory().get('/')
        view = VRCRegimentListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertSetEqual(
            set(queryset), {self.vrc_7th_regt, self.vrc_24th_regt},
            "VRCRegimentListView.get_queryset() should return all VRC regiments if no search_text supplied"
        )

        # If 'search_text' parameter supplied, get_queryset() should filter the default queryset
        request = RequestFactory().get('/', {'search_text': '7th'})
        view = VRCRegimentListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertSetEqual(
            set(queryset), {self.vrc_7th_regt},
            "VRCRegimentListView.get_queryset() should return VRC regiments whose names contain search_text"
        )
