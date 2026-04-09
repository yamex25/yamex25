from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guide', '0002_professional_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='decision',
            name='industry',
            field=models.CharField(choices=[('services', 'Professional Services'), ('trade', 'Retail / Trade'), ('manufacturing', 'Manufacturing / Production'), ('agriculture', 'Agriculture / Agro-trade'), ('hospitality', 'Hospitality / Tourism')], default='services', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='decision',
            name='company_name',
            field=models.CharField(blank=True, default='', max_length=120),
            preserve_default=False,
        ),
    ]
