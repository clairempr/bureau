from django.apps import AppConfig


class UsersAppConfig(AppConfig):

    name = "bureau.users"
    verbose_name = "Users"

    def ready(self):
        try:
            import users.signals  # noqa F401 pylint: disable=unused-import, import-outside-toplevel
        except ImportError:
            pass
