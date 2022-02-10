from factory import Faker
from factory.django import DjangoModelFactory

from ..models import Employee


class EmployeeFactory(DjangoModelFactory):
    """
    Base Employee factory
    """
    last_name = Faker('last_name')
    first_name = Faker('first_name')

    class Meta:
        model = Employee
