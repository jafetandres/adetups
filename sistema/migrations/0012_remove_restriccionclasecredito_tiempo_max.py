# Generated by Django 3.1.2 on 2021-04-07 18:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0011_remove_restriccionclasecredito_plazo_min'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restriccionclasecredito',
            name='tiempo_max',
        ),
    ]
