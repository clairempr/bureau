# Generated by Django 2.0.9 on 2018-11-25 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('military', '0001_initial'),
        ('personnel', '0005_auto_20181125_0322'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='vrc_units',
            field=models.ManyToManyField(related_name='employees', related_query_name='employee', to='military.Regiment'),
        ),
    ]
