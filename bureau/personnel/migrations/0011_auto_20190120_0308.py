# Generated by Django 2.0.9 on 2019-01-20 03:08

from django.db import migrations, models
import partial_date.fields


class Migration(migrations.Migration):

    dependencies = [
        ('personnel', '0010_auto_20190112_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='colored',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='confederate',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='date_of_birth',
            field=partial_date.fields.PartialDateField(blank=True, null=True),
        ),
    ]
