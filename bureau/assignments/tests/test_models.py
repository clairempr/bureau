from django.test import TestCase

from assignments.tests.factories import PositionFactory


class PositionTestCase(TestCase):
    """
    Test Position model
    """

    def test_str(self):
        """
        __str__ should return Position.title
        """

        title = 'Assistant to the Assistant Subassistant Commissioner'
        position = PositionFactory(title=title)
        self.assertEqual(str(position), title,
                        "Position.__str__ should be equal to Position.title")
