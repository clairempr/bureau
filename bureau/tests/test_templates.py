from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

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
            self.assertContains(response, text,
                                msg_prefix="Non-authenticated user should see '{}' in menu".format(text))

        User.objects.create_user(username='fred', password='secret')
        self.client.login(username='fred', password='secret')
        response = self.client.get(self.url)
        for text in ['My Profile', 'Sign Out']:
            self.assertContains(response, text,
                                msg_prefix="Non-authenticated user should see '{}' in menu".format(text))


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
        self.assertTrue(content_if_paginated in rendered,
                "If 'is_paginated' is in context, rendered html should contain '{}'".format(content_if_paginated))

        context = {'is_paginated': False,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=1)}
        rendered = render_to_string(self.template, context)
        self.assertFalse(content_if_paginated in rendered,
                "If 'is_paginated' not in context, rendered html shouldn't contain '{}'".format(content_if_paginated))

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
            self.assertIn(page_link.format(page_number=page_number), rendered,
                        '1st and last 2, and page numbers within 3 pages of current page should have a link to them')

        # Page numbers that are not the first 2 or last 2, or within 3 pages of current page should not have links
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=8)}
        partial_page_link = '<a class="page-link" href="?page={page_number}"> '
        for page_number in [3, 4, 12, 13]:
            self.assertFalse(partial_page_link.format(page_number=page_number) in rendered,
                             "Page numbers not 1st or last 2, or within 3 pages of current page, shouldn't have a link")

    def test_search_parameters(self):
        """
        If search criteria are in context, their values should be in the pagination
        """

        # If search text supplied, that should be in the link
        paginator = Paginator(object_list=['a', 'b'], per_page=1)
        search_text = 'That thing to search for'
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=1),
                   'search_text': search_text}
        rendered = render_to_string(self.template, context)
        self.assertTrue('&search_text={}'.format(search_text) in rendered,
                        "If search text supplied, that should be in link to the next page")

        # If search text supplied, that should be in the link to the previous page
        paginator = Paginator(object_list=['a', 'b'], per_page=1)
        search_text = 'That thing to search for'
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=2),
                   'search_text': search_text}
        rendered = render_to_string(self.template, context)
        self.assertTrue('&search_text={}'.format(search_text) in rendered,
                        "If search text supplied, that should be in link to the previous page")
