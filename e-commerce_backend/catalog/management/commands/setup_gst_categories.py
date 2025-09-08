from django.core.management.base import BaseCommand
from catalog.models import Category
from catalog.gst_rates import GST_RATES

class Command(BaseCommand):
    help = 'Setup categories with appropriate GST rates'

    def handle(self, *args, **options):
        categories_created = 0
        categories_updated = 0
        
        # Create/update categories with GST rates
        category_mappings = {
            'Electronics': 18.00,
            'Clothing & Fashion': 18.00,
            'Home & Kitchen': 18.00,
            'Books': 0.00,
            'Food & Beverages': 5.00,
            'Health & Personal Care': 18.00,
            'Sports & Outdoors': 18.00,
            'Toys & Games': 18.00,
            'Automotive': 28.00,
            'Mobile Phones': 12.00,
            'Computers': 12.00,
            'Home Appliances': 28.00,
            'Cosmetics': 18.00,
            'Medicines': 0.00,
            'Baby Products': 5.00,
            'Footwear': 18.00,  # Default, can be 5% for under ₹1000
            'Furniture': 18.00,
            'Bags & Luggage': 18.00,
            'Watches': 18.00,
            'Jewelry': 18.00,
            'Stationery': 18.00,
        }
        
        for category_name, gst_rate in category_mappings.items():
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'gst_rate': gst_rate}
            )
            
            if created:
                categories_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category_name} with GST rate: {gst_rate}%')
                )
            else:
                # Update GST rate if different
                if category.gst_rate != gst_rate:
                    category.gst_rate = gst_rate
                    category.save()
                    categories_updated += 1
                    self.stdout.write(
                        self.style.WARNING(f'Updated GST rate for {category_name}: {gst_rate}%')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Setup complete! Created: {categories_created}, Updated: {categories_updated} categories'
            )
        )