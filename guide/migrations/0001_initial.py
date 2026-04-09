from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Decision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.CharField(choices=[('accounting', 'Accounting Focus'), ('mixed', 'Finance + Operations'), ('operations', 'Full Operations')], max_length=20)),
                ('complexity', models.CharField(choices=[('low', 'Simple'), ('medium', 'Moderate'), ('high', 'Complex')], max_length=20)),
                ('growth', models.CharField(choices=[('stable', 'Stable'), ('growing', 'Growing'), ('scaling', 'Scaling')], max_length=20)),
                ('integration', models.CharField(choices=[('low', 'Minimal'), ('medium', 'Moderate'), ('high', 'High Integration')], max_length=20)),
                ('recommendation', models.CharField(max_length=100)),
                ('explanation', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
