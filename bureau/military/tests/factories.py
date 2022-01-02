from factory import DjangoModelFactory

from ..models import Regiment


class RegimentFactory(DjangoModelFactory):
    """
    Base Regiment factory
    """
    number = 15

    class Meta:
        model = Regiment
