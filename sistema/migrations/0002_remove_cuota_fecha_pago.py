# Generated by Django 3.1.2 on 2021-02-11 19:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cuota',
            name='fecha_pago',
        ),
    ]
