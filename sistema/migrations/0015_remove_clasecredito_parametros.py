# Generated by Django 3.1.2 on 2021-01-24 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0014_auto_20210124_1319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clasecredito',
            name='parametros',
        ),
    ]
