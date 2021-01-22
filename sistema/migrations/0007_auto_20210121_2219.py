# Generated by Django 3.1.2 on 2021-01-22 03:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0006_auto_20210121_2052'),
    ]

    operations = [
        migrations.RenameField(
            model_name='credito',
            old_name='cuota',
            new_name='cuotas',
        ),
        migrations.RemoveField(
            model_name='credito',
            name='crenrocob',
        ),
        migrations.RemoveField(
            model_name='credito',
            name='pagado',
        ),
        migrations.AlterField(
            model_name='credito',
            name='estado',
            field=models.CharField(max_length=3),
        ),
    ]
