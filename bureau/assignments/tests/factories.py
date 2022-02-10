from factory.django import DjangoModelFactory

from ..models import Assignment, Position


class AssignmentFactory(DjangoModelFactory):
    """
    Base Assignment factory
    """

    class Meta:
        model = Assignment


class PositionFactory(DjangoModelFactory):
    """
    Base Position factory
    """

    class Meta:
        model = Position
