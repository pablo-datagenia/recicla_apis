# Generated by Django 2.2.7 on 2021-01-10 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0023_auto_20210110_1503'),
    ]

    operations = [
        migrations.RenameField(
            model_name='solicitud',
            old_name='en_curso',
            new_name='en_viaje',
        ),
        migrations.AddField(
            model_name='viaje',
            name='modificado',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Modificado'),
        ),
    ]
