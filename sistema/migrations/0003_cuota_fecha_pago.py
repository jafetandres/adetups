# Generated by Django 3.1.2 on 2021-02-11 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0002_remove_cuota_fecha_pago'),
    ]

    operations = [
        migrations.AddField(
            model_name='cuota',
            name='fecha_pago',
            field=models.DateField(default=None),
            preserve_default=False,
        ),
    ]