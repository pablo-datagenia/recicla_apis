# Generated by Django 2.2.7 on 2021-01-09 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0013_auto_20210109_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material',
            name='codigo',
            field=models.CharField(max_length=2, unique=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='material',
            field=models.CharField(max_length=150, unique=True),
        ),
        migrations.AlterField(
            model_name='solicitud',
            name='punto',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='apis.PuntoRecoleccion'),
        ),
    ]
