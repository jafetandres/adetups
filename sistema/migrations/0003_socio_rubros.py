# Generated by Django 3.1.2 on 2021-01-16 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0002_auto_20210116_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='socio',
            name='rubros',
            field=models.ManyToManyField(blank=True, null=True, to='sistema.RubroSocio'),
        ),
    ]
