from factory import DjangoModelFactory

from ..models import Assignment


class AssignmentFactory(DjangoModelFactory):
    """
    Base Assignment factory
    """

    class Meta:
        model = Assignment
