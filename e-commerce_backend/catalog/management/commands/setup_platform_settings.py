from django.core.management.base import BaseCommand
from catalog.models import PlatformSettings

class Command(BaseCommand):
    help = 'Setup initial platform settings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--commission-rate',
            type=float,
            default=5.0,
            help='Set platform commission rate (default: 5.0%)'
        )

    def handle(self, *args, **options):
        commission_rate = options['commission_rate']
        
        # Create or update platform settings
        settings, created = PlatformSettings.objects.get_or_create(
            id=1,  # Ensure only one settings record
            defaults={'commission_rate': commission_rate}
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created platform settings with commission rate: {commission_rate}%')
            )
        else:
            settings.commission_rate = commission_rate
            settings.save()
            self.stdout.write(
                self.style.WARNING(f'Updated platform commission rate to: {commission_rate}%')
            )