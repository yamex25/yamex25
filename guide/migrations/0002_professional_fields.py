from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guide', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='decision',
            name='business_size',
            field=models.CharField(choices=[('small', 'Small / Emerging'), ('medium', 'Mid-market'), ('large', 'Large / Complex')], default='small', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='decision',
            name='budget',
            field=models.CharField(choices=[('rapid', 'Fast launch / constrained budget'), ('balanced', 'Balanced cost and timeline'), ('strategic', 'Strategic investment / transformation')], default='balanced', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='decision',
            name='compliance',
            field=models.CharField(choices=[('standard', 'Standard local compliance'), ('regional', 'Regional or multi-office'), ('global', 'Global / multi-entity compliance')], default='standard', max_length=20),
            preserve_default=False,
        ),
    ]
