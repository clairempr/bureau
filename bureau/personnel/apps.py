from django.apps import AppConfig


class PersonnelConfig(AppConfig):
    name = 'bureau.personnel'

    def ready(self):
        from . import signals

