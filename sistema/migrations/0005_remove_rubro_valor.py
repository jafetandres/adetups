# Generated by Django 3.1.2 on 2021-04-02 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0004_auto_20210211_2336'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rubro',
            name='valor',
        ),
    ]
