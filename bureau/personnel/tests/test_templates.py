from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.test import TestCase

from medical.tests.factories import AilmentFactory, AilmentTypeFactory
from personnel.tests.factories import EmployeeFactory


class EmployeeListViewTemplateTestCase(TestCase):
    """
    Test template of personnel.views.EmployeeListView
    """

    def setUp(self):
        self.template = 'personnel/employee_list.html'

    def test_template(self):
        last_name = 'Howard'
        first_name = 'Oliver Otis'

        employee = EmployeeFactory(first_name='Oliver Otis', last_name='Howard')

        context = {'last_name': last_name, 'first_name': first_name, 'employee_list': [employee]}
        rendered = render_to_string(self.template, context)

        # "Bureau Employees" should be in html
        text = 'Bureau Employees'
        self.assertTrue(text in rendered, "'{}' should be in {}".format(text, self.template))

        # Search criteria should be in html
        for key in ['last_name', 'first_name']:
            self.assertTrue(key in rendered, "'{}' should be in {}".format(text, self.template))

        # Employees should be listed
        self.assertTrue(str(employee) in rendered, 'Employees should be listed in {}'.format(self.template))


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
        page_header = page_header_no_employees.format(ailment=ailment)
        self.assertInHTML(page_header, rendered,
                          msg_prefix='Employees With <Ailment> should be in page header if no employees with ailment')

        # "Employees With <AilmentType>" should be in html if 'ailment' is an AilmentType and no employees found
        context = {'ailment': ailment_type}
        rendered = render_to_string(self.template, context)
        page_header = page_header_no_employees.format(ailment=ailment_type)
        self.assertInHTML(page_header, rendered,
                msg_prefix='Employees With <AilmentType> should be in page header if no employees with ailment type')

        # "Employees With <Ailment> (count)" should be in html
        paginator = Paginator(object_list=[employee], per_page=1)
        context = {'ailment': ailment,
                   'employee_list': paginator.object_list,
                   'paginator': paginator}
        rendered = render_to_string(self.template, context)
        page_header = page_header_with_employees.format(ailment=ailment, count=len(paginator.object_list))
        self.assertInHTML(page_header, rendered,
                msg_prefix='Employees With <Ailment> (<count>) should be in page header if employees with ailment type')

        # Employees should be listed
        self.assertTrue(employee.first_name in rendered, 'Employees should be listed in {}'.format(self.template))
        self.assertTrue(employee.last_name in rendered, 'Employees should be listed in {}'.format(self.template))
