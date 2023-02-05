from django.core.management.base import BaseCommand

from personnel.models import Employee


class Command(BaseCommand):
    help = "Sets 'needs_backfilling' for all Employees"

    def add_arguments(self, parser):
        parser.add_argument('value', type=bool,
                            help="Indicates whether 'needs_backfilling' should be set to True or False")

    def handle(self, *args, **kwargs):
        value = kwargs['value']
        Employee.objects.all().update(needs_backfilling=value)
