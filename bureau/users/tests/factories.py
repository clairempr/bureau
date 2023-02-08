from typing import Any, Sequence

from django.contrib.auth import get_user_model
from factory import Faker, post_generation
from factory.django import DjangoModelFactory
from factory.faker import faker


class UserFactory(DjangoModelFactory):

    username = Faker("user_name")
    email = Faker("email")
    name = Faker("name")

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):  # pylint: disable=unused-argument
        fake = faker.Faker()
        password = fake.password()
        self.set_password(password)

    class Meta:
        model = get_user_model()
        django_get_or_create = ["username"]
