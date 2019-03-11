# Generated by Django 2.0.9 on 2019-01-10 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('military', '0002_regiment_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='regiment',
            name='branch',
            field=models.CharField(choices=[('INF', 'Infantry'), ('CAV', 'Cavalry'), ('ART', 'Artillery')], default='INF', max_length=3),
        ),
    ]