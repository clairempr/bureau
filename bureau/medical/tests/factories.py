from factory import DjangoModelFactory, SubFactory

from ..models import Ailment, AilmentType


class AilmentTypeFactory(DjangoModelFactory):
    """
    Base AilmentType factory
    """

    class Meta:
        model = AilmentType


class AilmentFactory(DjangoModelFactory):
    """
    Base Ailment factory
    """

    type = SubFactory(AilmentTypeFactory)

    class Meta:
        model = Ailment
