# Generated by Django 3.1.2 on 2021-02-11 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0005_auto_20210210_2011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitudcredito',
            name='fecha_ingreso',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
