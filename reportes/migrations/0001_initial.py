# Generated by Django 3.1.2 on 2021-09-29 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ReporteSolicitudCredito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(default='logo_adetups.png', upload_to='reportes/img')),
            ],
        ),
    ]
