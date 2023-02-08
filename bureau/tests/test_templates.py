from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from medical.tests.factories import AilmentFactory
from places.tests.factories import BureauStateFactory

User = get_user_model()


class BaseTemplateTestCase(SimpleTestCase):
    """
    Test Home page
    """

    def setUp(self):
        self.template = 'base.html'

    def test_template_content(self):
        message = 'This is a message'
        context = {'messages': [message]}

        rendered = render_to_string(self.template, context)
        self.assertInHTML(message, rendered, msg_prefix="If messages in context, they should be displayed on the page")

        content_block_placeholder = 'Use this document as a way to quick start any new project.'
        rendered = render_to_string(self.template)
        self.assertInHTML(content_block_placeholder, rendered,
                          msg_prefix="Base template should contain content block placeholder text")


class HomeTemplateTestCase(TestCase):
    """
    Test Home page
    """

    def setUp(self):
        self.url = reverse('home')
        self.template = 'pages/home.html'

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template)


class MainNavMenyTemplateTestCase(TestCase):
    """
    Test main nav menu template main_nav_menu.html
    """

    def setUp(self):
        self.url = reverse('home')
        self.template = 'main_nav_menu.html'

    def test_template_content(self):
        rendered = render_to_string(self.template, context={})
        for nav in ['The Bureau', 'Employees',
                    'Statistics', 'General', 'Detailed', 'State Comparison',
                    'Bureau States', 'Regiments', 'About']:
            self.assertIn(nav, rendered)

    def test_authenticated_content(self):
        # Non-authenticated user should see "Sign Up" and "Sign In" in menu
        response = self.client.get(self.url)
        for text in ['Sign Up', 'Sign In']:
            self.assertContains(response, text, msg_prefix=f"Non-authenticated user should see '{text}' in menu")

        User.objects.create_user(username='fred', password='secret')
        self.client.login(username='fred', password='secret')
        response = self.client.get(self.url)
        for text in ['My Profile', 'Sign Out']:
            self.assertContains(response, text, msg_prefix=f"Non-authenticated user should see '{text}' in menu")


class PaginationTemplateTestCase(SimpleTestCase):
    """
    Test partial template pagination.html
    """

    def setUp(self):
        self.template = 'partials/pagination.html'

    def test_paginated_or_not(self):
        """
        If 'is_paginated' is in context, rendered html should contain "Search results pages"
        """
        content_if_paginated = 'Search results pages'

        paginator = Paginator(object_list=['a'], per_page=1)
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=1)}
        rendered = render_to_string(self.template, context)
        self.assertTrue(
            content_if_paginated in rendered,
            f"If 'is_paginated' is in context, rendered html should contain '{content_if_paginated}'"
        )

        context = {'is_paginated': False,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=1)}
        rendered = render_to_string(self.template, context)
        self.assertFalse(
            content_if_paginated in rendered,
            f"If 'is_paginated' not in context, rendered html shouldn't contain '{content_if_paginated}'"
        )

    def test_page_obj_has_previous_or_not(self):
        """
        If there's a previous page, there should be a link to the previous page:
            <a class="page-link" href="?page={{ page_obj.previous_page_number }}

        If there's no previous page, there should be a <span class="page-link">&laquo;</span>
        """

        disabled_previous_page = '<span class="page-link">&laquo;</span>'
        previous_page_link = '<a class="page-link" href="?page=1'

        # If there's a previous page, there should be a link to the previous page
        paginator = Paginator(object_list=['a', 'b'], per_page=1)
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=2)}
        rendered = render_to_string(self.template, context)
        self.assertIn(previous_page_link, rendered)
        self.assertFalse(disabled_previous_page in rendered,
                         "If there's a previous page, there should be no disabled 'previous page'")

        # If there's no previous page, there should be a disabled "previous page"
        paginator = Paginator(object_list=['a'], per_page=1)
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=1)}
        rendered = render_to_string(self.template, context)
        self.assertTrue(disabled_previous_page in rendered,
                        "If there's no previous page, there should be a disabled 'previous page'")
        self.assertFalse(previous_page_link in rendered,
                         "If there's no previous page, there should be no link to a previous page")

    def test_page_obj_has_next_or_not(self):
        """
        If there's a next page, there should be a link to the next page:
            <a class="page-link" href="?page={{ page_obj.next_page_number }}

        If there's no next page, there should be a <span class="page-link">&raquo;</span>
        """

        disabled_next_page = '<span class="page-link">&raquo;</span>'
        next_page_link = '<a class="page-link" href="?page=2'

        # If there's a next page, there should be a link to the next page
        paginator = Paginator(object_list=['a', 'b'], per_page=1)
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=1)}
        rendered = render_to_string(self.template, context)
        self.assertIn(next_page_link, rendered)
        self.assertFalse(disabled_next_page in rendered,
                         "If there's a next page, there should be no disabled 'next page'")

        # If there's no next page, there should be a disabled "next page"
        paginator = Paginator(object_list=['a'], per_page=1)
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=1)}
        rendered = render_to_string(self.template, context)
        self.assertTrue(disabled_next_page in rendered,
                        "If there's no next page, there should be a disabled 'next page'")
        self.assertFalse(next_page_link in rendered,
                         "If there's no next page, there should be no link to a next page")

    def test_paginator_page_range(self):
        """
        The current page should be marked with <span class="visually-hidden">(current)</span>

        Otherwise for page numbers that are within 3 pages of the current page, there should be a link to them,
        with search text if it's in context
        """

        paginator = Paginator(object_list=['x' for i in range(15)], per_page=1)
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=8)}
        rendered = render_to_string(self.template, context)

        # Current page (8) should be marked "(current)" for screen reader
        current_page_span = '<span class="page-link">8 <span class="visually-hidden">(current)</span></span>'
        self.assertInHTML(current_page_span, rendered,
                          msg_prefix="Current page number should be marked with '(current)' for screen reader")

        # First 2 and last 2 page numbers (1-2 and 14-15),
        # and page numbers within 3 pages of current page (5-7 and 9-11) should have a link to them
        page_link = '<a class="page-link" href="?page={page_number}'
        for page_number in [1, 2, 5, 6, 7, 9, 10, 11, 14, 15]:
            self.assertIn(
                page_link.format(page_number=page_number), rendered,
                '1st and last 2, and page numbers within 3 pages of current page should have a link to them'
            )

        # Page numbers that are not the first 2 or last 2, or within 3 pages of current page should not have links
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=8)}
        partial_page_link = '<a class="page-link" href="?page={page_number}"> '
        for page_number in [3, 4, 12, 13]:
            self.assertFalse(partial_page_link.format(page_number=page_number) in rendered,
                             "Page numbers not 1st or last 2, or within 3 pages of current page, shouldn't have a link")


class SearchParametersTemplateTestCase(TestCase):
    """
    Test search_parameters.html template
    """

    def setUp(self):
        self.template = 'partials/search_parameters.html'

    def test_search_text(self):
        """
        If search_text is in context, its value should be in the pagination
        """
        search_text = 'That thing to search for'
        context = {'search_text': search_text}
        rendered = render_to_string(self.template, context)
        self.assertTrue(f'&search_text={search_text}' in rendered, 'If search text supplied, that should be in link')

    def test_name(self):
        """
        If search_text is in context, its value should be in the pagination
        """
        last_name = 'Last Name'
        first_name = 'First Name'
        context = {'last_name': last_name, 'first_name': first_name}
        rendered = render_to_string(self.template, context)
        self.assertTrue(f'&last_name={last_name}' in rendered, 'If last name supplied, that should be in link')
        self.assertTrue(f'&first_name={first_name}' in rendered, 'If first name supplied, that should be in link')

    def test_gender(self):
        """
        If gender is in context, its value should be in the pagination
        """
        gender = 'Female'
        context = {'gender': gender}
        rendered = render_to_string(self.template, context)
        self.assertTrue(f'&gender={gender}' in rendered, 'If gender supplied, that should be in link')

    def test_place_of_birth(self):
        """
        If search_text is in context, its value should be in the pagination
        """
        place_of_birth = 'New York'
        context = {'place_of_birth': place_of_birth}
        rendered = render_to_string(self.template, context)
        self.assertTrue(f'&place_of_birth={place_of_birth}' in rendered,
                        'If place_of_birth supplied, that should be in link')

    def test_place_of_death(self):
        """
        If search_text is in context, its value should be in the pagination
        """
        place_of_death = 'New York'
        context = {'place_of_death': place_of_death}
        rendered = render_to_string(self.template, context)
        self.assertTrue(f'&place_of_death={place_of_death}' in rendered,
                        'If place_of_death supplied, that should be in link')

    def test_bureau_state(self):
        """
        If bureau_states is in context, its value should be in the pagination
        """
        alabama = BureauStateFactory(name='Alabama')
        arkansas = BureauStateFactory(name='Arkansas')

        # bureau_states is list of tuples: (state, selected)
        bureau_states = [(alabama, False), (arkansas, True)]
        context = {'bureau_states': bureau_states}
        rendered = render_to_string(self.template, context)
        self.assertTrue(f'&bureau_states={arkansas.pk}' in rendered,
                        'If bureau_states supplied, selected states should be in link')

    def test_ailment(self):
        """
        If ailments is in context, its value should be in the pagination
        """
        shell_wound = AilmentFactory(name='Shell wound')
        hernia = AilmentFactory(name='hernia')

        # ailments is list of tuples: (ailment, selected)
        ailments = [(shell_wound, False), (hernia, True)]
        context = {'ailments': ailments}
        rendered = render_to_string(self.template, context)
        self.assertTrue(f'&ailments={hernia.pk}' in rendered,
                        'If ailments supplied, selected ailments should be in link')

    def test_booleans(self):
        """
        If a boolean is in context, its value should be in the pagination
        """
        for key in ['vrc', 'union_veteran', 'confederate_veteran', 'colored', 'died_during_assignment',
                    'former_slave', 'slaveholder']:
            context = {key: key}
            rendered = render_to_string(self.template, context)
            self.assertTrue(f'&{key}={key}' in rendered, f'If {key} supplied, that should be in link')
