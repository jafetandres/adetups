# Generated by Django 3.1.2 on 2021-09-29 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reportes', '0002_auto_20210929_1009'),
    ]

    operations = [
        migrations.AddField(
            model_name='reporteconfiguracion',
            name='descripcion',
            field=models.CharField(default='', max_length=100),
        ),
    ]
