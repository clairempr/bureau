from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.test import TestCase

from medical.tests.factories import AilmentFactory, AilmentTypeFactory
from personnel.tests.factories import EmployeeFactory
from places.tests.factories import BureauStateFactory


class EmployeeListViewTemplateTestCase(TestCase):
    """
    Test template of personnel.views.EmployeeListView
    """

    def setUp(self):
        self.template = 'personnel/employee_list.html'

    def test_name_in_template(self):
        last_name = 'Howard'
        first_name = 'Oliver Otis'

        employee = EmployeeFactory(first_name='Oliver Otis', last_name='Howard')

        context = {'last_name': last_name, 'first_name': first_name, 'employee_list': [employee]}
        rendered = render_to_string(self.template, context)

        # "Bureau Employees" should be in html
        text = 'Bureau Employees'
        self.assertTrue(text in rendered, f"'{text}' should be in {self.template}")

        # Search criteria should be in html
        for key in ['last_name', 'first_name']:
            self.assertTrue(key in rendered, f"'{text}' should be in {self.template}")

        # Employees should be listed
        self.assertTrue(str(employee) in rendered, 'Employees should be listed in {self.template}')

        # If VRC or has Bureau states, that should be in parentheses after name
        vrc_employee = EmployeeFactory(vrc=True)
        vrc_employee.bureau_states.add(BureauStateFactory(name='Missouri'))
        context = {'employee_list': [vrc_employee]}
        rendered = render_to_string(self.template, context)
        self.assertIn('(VRC - Missouri)', rendered)

    def test_gender_in_template(self):
        rendered = render_to_string(self.template, context={})

        for text in ['Gender', 'Male', 'Female']:
            self.assertTrue(text in rendered, f"{text} should be in page")

    def test_bureau_state_in_template(self):
        bureau_state = BureauStateFactory(name='Tarheel State')
        EmployeeFactory()

        context = {'bureau_states': [(bureau_state, True)]}
        rendered = render_to_string(self.template, context)

        # Bureau states should be in html
        self.assertTrue('Tarheel State' in rendered, "Bureau state should be in page")

    def test_ailment_in_template(self):
        ailment = AilmentFactory(name='Consumption')
        EmployeeFactory()

        context = {'ailments': [(ailment, True)]}
        rendered = render_to_string(self.template, context)

        # Ailments states should be in html
        self.assertTrue('Consumption' in rendered, "Ailment should be in page")

    def test_misc_labels_in_template(self):
        rendered = render_to_string(self.template, context={})

        for label in ['VRC', 'Union veteran', 'Confederate veteran', 'Identified as "Colored"',
                      'Died during assignment', 'Former slave', 'Former slaveholder', 'Place of birth',
                      'Year of birth', 'Place of death']:
            self.assertTrue(label in rendered, f"{label} should be in page")


class EmployeesWithAilmentListViewTemplateTestCase(TestCase):
    """
    Test template of personnel.views.EmployeesWithAilmentListView
    """

    def setUp(self):
        self.template = 'personnel/employees_with_ailment_list.html'

    def test_template(self):
        page_header_no_employees = '<div class="page-header">Employees With {ailment}</div>'
        page_header_with_employees = '<div class="page-header">Employees With {ailment} ({count})</div>'

        ailment_type = AilmentTypeFactory(name='Headache')
        ailment = AilmentFactory(name='Migraine', type=ailment_type)
        employee = EmployeeFactory()

        # "Employees With <Ailment>" should be in page header if 'ailment' is an Ailment and no employees found
        context = {'ailment': ailment}
        rendered = render_to_string(self.template, context)
        page_header = page_header_no_employees.format(ailment=ailment)  # pylint: disable=consider-using-f-string, useless-suppression
        self.assertInHTML(page_header, rendered,
                          msg_prefix='Employees With <Ailment> should be in page header if no employees with ailment')

        # "Employees With <AilmentType>" should be in html if 'ailment' is an AilmentType and no employees found
        context = {'ailment': ailment_type}
        rendered = render_to_string(self.template, context)
        page_header = page_header_no_employees.format(ailment=ailment_type)  # pylint: disable=consider-using-f-string, useless-suppression
        self.assertInHTML(
            page_header, rendered,
            msg_prefix='Employees With <AilmentType> should be in page header if no employees with ailment type'
        )

        # "Employees With <Ailment> (count)" should be in html
        paginator = Paginator(object_list=[employee], per_page=1)
        context = {'ailment': ailment,
                   'employee_list': paginator.object_list,
                   'paginator': paginator}
        rendered = render_to_string(self.template, context)
        page_header = page_header_with_employees.format(ailment=ailment, count=len(paginator.object_list))  # pylint: disable=consider-using-f-string, useless-suppression
        self.assertInHTML(
            page_header, rendered,
            msg_prefix='Employees With <Ailment> (<count>) should be in page header if employees with ailment type'
        )

        # Employees should be listed
        self.assertTrue(employee.first_name in rendered, f'Employees should be listed in {self.template}')
        self.assertTrue(employee.last_name in rendered, f'Employees should be listed in {self.template}')
