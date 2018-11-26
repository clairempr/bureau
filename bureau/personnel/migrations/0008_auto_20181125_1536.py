# Generated by Django 2.0.9 on 2018-11-25 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personnel', '0007_auto_20181125_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='bureau_states',
            field=models.ManyToManyField(blank=True, limit_choices_to={'bureau_operations': True}, related_name='employees', related_query_name='employee', to='places.Region'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='regiments',
            field=models.ManyToManyField(blank=True, related_name='employees', related_query_name='employee', to='military.Regiment'),
        ),
    ]