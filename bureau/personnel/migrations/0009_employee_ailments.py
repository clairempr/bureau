# Generated by Django 2.0.9 on 2019-01-05 03:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medical', '0001_initial'),
        ('personnel', '0008_auto_20181125_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='ailments',
            field=models.ManyToManyField(blank=True, related_name='employees', related_query_name='employee', to='medical.Ailment'),
        ),
    ]
