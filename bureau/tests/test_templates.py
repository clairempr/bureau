from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class BaseTemplateTestCase(TestCase):
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

    def test_template_content(self):
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

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template)


class PaginationTemplateTestCase(TestCase):
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

        rendered = render_to_string(self.template, {'is_paginated': True})
        self.assertTrue(content_if_paginated in rendered,
                "If 'is_paginated' is in context, rendered html should contain '{}'".format(content_if_paginated))

        rendered = render_to_string(self.template, {'is_paginated': False})
        self.assertFalse(content_if_paginated in rendered,
                "If 'is_paginated' not in context, rendered html shouldn't contain '{}'".format(content_if_paginated))

    def test_page_obj_has_previous_or_not(self):
        """
        If there's a previous page, there should be a link to the previous page, with search_text if it's in context:
            <a class="page-link" href="?page={{ page_obj.previous_page_number }}
            {% if search_text %}&search_text={{ search_text }}{% endif %}">&laquo;</a>

        If there's no previous page, there should be a <span class="page-link">&laquo;</span>
        """

        disabled_previous_page = '<span class="page-link">&laquo;</span>'
        previous_page_link = 'href="?page=1"'

        # If there's a previous page, there should be a link to the previous page
        paginator = Paginator(object_list=['a', 'b'], per_page=1)
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=2)}
        rendered = render_to_string(self.template, context)
        self.assertTrue(previous_page_link in rendered,
                        "If there's a previous page, there should be a link to the previous page")
        self.assertFalse(disabled_previous_page in rendered,
                          "If there's a previous page, there should be no disabled 'previous page'")

        # If search text supplied, that should be in the link
        search_text = 'That thing to search for'
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=2),
                   'search_text': search_text}
        rendered = render_to_string(self.template, context)
        self.assertTrue('&search_text={}'.format(search_text) in rendered,
                        "If search text supplied, that should be in link to the previous page")

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
        If there's a next page, there should be a link to the next page, with search_text if it's in context:
            <a class="page-link" href="?page={{ page_obj.next_page_number }}
              {% if search_text %}&search_text={{ search_text }}{% endif %}">&raquo;</a>

        If there's no next page, there should be a <span class="page-link">&raquo;</span>
        """

        disabled_next_page = '<span class="page-link">&raquo;</span>'
        next_page_link = 'href="?page=2"'

        # If there's a next page, there should be a link to the next page
        paginator = Paginator(object_list=['a', 'b'], per_page=1)
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=1)}
        rendered = render_to_string(self.template, context)
        self.assertTrue(next_page_link in rendered, "If there's a next page, there should be a link to the next page")
        self.assertFalse(disabled_next_page in rendered,
                          "If there's a next page, there should be no disabled 'next page'")

        # If search text supplied, that should be in the link
        search_text = 'That thing to search for'
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=1),
                   'search_text': search_text}
        rendered = render_to_string(self.template, context)
        self.assertTrue('&search_text={}'.format(search_text) in rendered,
                        "If search text supplied, that should be in link to the next page")

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

    def test_ellipse_before_page_numbers(self):
        """
        If current page number > 5, there should be an ellipse before the list of page numbers
        """

        ellipse = '&hellip;'
        paginator = Paginator(object_list=['a', 'b', 'c', 'd', 'e', 'f'], per_page=1)

        # Current page > 6: there should be an ellipse
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=6)}
        rendered = render_to_string(self.template, context)
        self.assertTrue(ellipse in rendered,
                        "If current page number > 5, there should be an ellipse before the list of page numbers")

        # Current page is 5: there should be no ellipse
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=5)}
        rendered = render_to_string(self.template, context)
        self.assertFalse(ellipse in rendered,
                        "If current page number is 5, there should be no ellipse before the list of page numbers")

        # Current page < 5: there should be no ellipse
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=4)}
        rendered = render_to_string(self.template, context)
        self.assertFalse(ellipse in rendered,
                        "If current page number < 5, there should be no ellipse before the list of page numbers")

    def test_ellipse_after_page_numbers(self):
        """
        If total number of pages > current page number + 4, there should be an ellipse before the list of page numbers
        """

        ellipse = '&hellip;'
        paginator = Paginator(object_list=['a', 'b', 'c', 'd', 'e', 'f'], per_page=1)

        # Current page is 1 (out of 6 pages): there should be an ellipse
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=1)}
        rendered = render_to_string(self.template, context)
        self.assertTrue(ellipse in rendered,
                        "If current page number is 1 (of 6), there should be an ellipse after the list of page numbers")

        # Current page is 2 (of 6): there should be no ellipse
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=2)}
        rendered = render_to_string(self.template, context)
        self.assertFalse(ellipse in rendered,
                        "If current page number is 2 (of 6), there should be no ellipse after the list of page numbers")

        # Current page is 3 (of 6): there should be no ellipse
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=3)}
        rendered = render_to_string(self.template, context)
        self.assertFalse(ellipse in rendered,
                        "If current page number is 3 (of 6), there should be no ellipse after the list of page numbers")

    def test_paginator_page_range(self):
        """
        The current page should be marked with <span class="sr-only">(current)</span>

        Otherwise for page numbers that are within 4 pages of the current page, there should be a link to them,
        with search text if it's in context
        """

        paginator = Paginator(object_list=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k'], per_page=1)
        context = {'is_paginated': True,
                   'paginator': paginator,
                   'page_obj': paginator.page(number=6)}
        rendered = render_to_string(self.template, context)

        # Current page (6) should be marked "(current)" for screen reader
        current_page_span = '<span class="page-link">6 <span class="sr-only">(current)</span></span>'
        self.assertInHTML(current_page_span, rendered,
                          msg_prefix="Current page number should be marked with '(current)' for screen reader")

        # Page numbers within 4 pages of current page (2-5 and 7-10) should have a link to them
        page_link = '<a class ="page-link" href="?page={page_number}">{page_number}</a>'
        for page_number in [2, 3, 4, 5, 7, 8, 9, 10]:
            self.assertInHTML(page_link.format(page_number=page_number), rendered,
                              msg_prefix='Page numbers within 4 pages of current page should have a link to them')

        # Page numbers outside of 4-page range (1 and 11) should not have a link to them without an ellipse
        # Check for space after, because of the ellipse
        partial_page_link = '<a class="page-link" href="?page={page_number}"> '
        for page_number in [1, 11]:
            self.assertFalse(partial_page_link.format(page_number=page_number) in rendered,
                             "Page numbers outside of 4-page range of current page shouldn't have a link without ...")

        # Page numbers within 4 pages of current page (2-5 and 7-10) should have a link to them with search text
        # if present in context
        search_text = 'That thing to search for'
        context['search_text'] = search_text
        rendered = render_to_string(self.template, context)

        page_link = '<a class ="page-link" href="?page={page_number}&search_text={search_text}">{page_number}</a>'
        for page_number in [2, 3, 4, 5, 7, 8, 9, 10]:
            self.assertInHTML(page_link.format(page_number=page_number, search_text=search_text), rendered,
                              msg_prefix='Page numbers within 4 pages of current page should have a link with search text')
