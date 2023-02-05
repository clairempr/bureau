from django.test import TestCase

from military.tests.factories import RegimentFactory


class RegimentTestCase(TestCase):
    """
    Test Regiment model
    """

    def test_str(self):
        """
        If __str__ should return Regiment.name
        """

        regiment = RegimentFactory(name='3rd Maine Volunteer Infantry Regiment')
        self.assertEqual(str(regiment), regiment.name,
                         "Regiment.__str__ should be equal to Regiment.name")
