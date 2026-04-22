from django.core.management.base import BaseCommand
from guide.models import Industry


class Command(BaseCommand):
    help = 'Create default industries for the ERP decision guide'

    def handle(self, *args, **options):
        industries = [
            {'name': 'Professional Services',
                'description': 'Consulting, legal, accounting, and other professional services'},
            {'name': 'Retail & Trade',
                'description': 'Retail stores, wholesale, and trading businesses'},
            {'name': 'Manufacturing',
                'description': 'Production and manufacturing operations'},
            {'name': 'Agriculture',
                'description': 'Farming, agro-processing, and agricultural trade'},
            {'name': 'Hospitality & Tourism',
                'description': 'Hotels, restaurants, and tourism services'},
            {'name': 'Healthcare',
                'description': 'Medical practices, clinics, and healthcare services'},
            {'name': 'Education',
                'description': 'Schools, universities, and educational institutions'},
            {'name': 'Construction',
                'description': 'Building, construction, and real estate development'},
            {'name': 'Technology',
                'description': 'Software, IT services, and technology companies'},
            {'name': 'Transportation & Logistics',
                'description': 'Shipping, logistics, and transportation services'},
            {'name': 'Financial Services',
                'description': 'Banks, insurance, and financial institutions'},
            {'name': 'Other', 'description': 'Other industries not listed above'},
        ]

        for industry_data in industries:
            industry, created = Industry.objects.get_or_create(
                name=industry_data['name'],
                defaults={
                    'description': industry_data['description'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Created industry: {industry.name}'))
            else:
                self.stdout.write(f'Industy already exists: {industry.name}')
