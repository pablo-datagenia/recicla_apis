# Generated by Django 2.2.7 on 2021-01-09 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0007_solicitud_domicilio'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitud',
            name='materiales',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
