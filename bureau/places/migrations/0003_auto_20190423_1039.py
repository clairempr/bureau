# Generated by Django 2.0.9 on 2019-04-23 10:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0002_place'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='place',
            unique_together={('city', 'region', 'country')},
        ),
    ]
