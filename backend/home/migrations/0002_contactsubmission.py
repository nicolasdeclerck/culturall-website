# Generated manually for issue #7

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('subject', models.CharField(max_length=255, verbose_name='Sujet')),
                ('message', models.TextField(verbose_name='Message')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de soumission')),
            ],
            options={
                'verbose_name': 'Demande de contact',
                'verbose_name_plural': 'Demandes de contact',
                'ordering': ['-created_at'],
            },
        ),
    ]
