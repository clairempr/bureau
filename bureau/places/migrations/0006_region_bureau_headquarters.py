# Generated by Django 2.2.9 on 2021-09-05 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0005_auto_20190708_0158'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='bureau_headquarters',
            field=models.BooleanField(default=False),
        ),
    ]
