from django.core.management.base import BaseCommand
from micro_admin.models import LoanRepaymentEvery


class Command(BaseCommand):
    help = 'Creates Loan Repayment Every'

    def handle(self, *args, **options):
        for i in range(1, 6):
            LoanRepaymentEvery.objects.get_or_create(value=i)
        self.stdout.write('Successfully Created Loan Repayment Every.')
