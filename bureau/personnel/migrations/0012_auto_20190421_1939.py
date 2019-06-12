# Generated by Django 2.0.9 on 2019-04-21 19:39

from django.db import migrations, models
import django.db.models.deletion
import partial_date.fields


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0002_place'),
        ('personnel', '0011_auto_20190120_0308'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='date_of_death',
            field=partial_date.fields.PartialDateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='died_during_assignment',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='former_slave',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='needs_backfilling',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='penmanship_contest',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='place_of_birth',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees_born_in', to='places.Place'),
        ),
        migrations.AddField(
            model_name='employee',
            name='place_of_death',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees_died_in', to='places.Place'),
        ),
        migrations.AddField(
            model_name='employee',
            name='place_of_residence',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employees_residing_in', to='places.Place'),
        ),
        migrations.AddField(
            model_name='employee',
            name='slaveholder',
            field=models.BooleanField(default=False),
        ),
    ]