from django.core.management.base import BaseCommand
from django.db import transaction
from Members.models import Payment

class Command(BaseCommand):
    help = 'Fix payment status for existing data where Payment_Balance > 0'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        # Find problematic payments
        invalid_payments = Payment.objects.filter(
            Payment_Balance__gt=0,
            Payment_Status=True
        )
        
        count = invalid_payments.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('No payments need to be fixed!')
            )
            return
        
        self.stdout.write(f'Found {count} payments to fix:')
        
        # Show details of what will be updated
        for payment in invalid_payments[:10]:  # Show first 10 as example
            self.stdout.write(
                f'  Payment ID: {payment.id}, Balance: {payment.Payment_Balance}, '
                f'Member: {payment.Member}, Amount: {payment.Amount}'
            )
        
        if count > 10:
            self.stdout.write(f'  ... and {count - 10} more')
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('DRY RUN: No changes made')
            )
            return
        
        # Confirm before proceeding
        confirm = input(f'Update {count} payment records? (y/N): ')
        if confirm.lower() != 'y':
            self.stdout.write('Operation cancelled')
            return
        
        # Perform the update
        with transaction.atomic():
            updated_count = invalid_payments.update(Payment_Status=False)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} payment records'
                )
            )
