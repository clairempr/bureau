# Generated by Django 4.0.10 on 2023-10-17 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0008_auto_20220209_1727'),
        ('assignments', '0012_remove_assignment_bureau_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='bureau_states',
            field=models.ManyToManyField(blank=True, limit_choices_to={'bureau_operations': True}, related_name='assignments', related_query_name='assignment', to='places.region', verbose_name='bureau states (jurisdiction)'),
        ),
    ]