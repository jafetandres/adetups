# Generated by Django 3.1.2 on 2021-04-23 01:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0014_auto_20210422_1955'),
    ]

    operations = [
        migrations.RenameField(
            model_name='solicitudcredito',
            old_name='revisado_por',
            new_name='revisada_por',
        ),
        migrations.RemoveField(
            model_name='solicitudcredito',
            name='aprobado_por',
        ),
        migrations.AddField(
            model_name='solicitudcredito',
            name='aprobada_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='aprobado_por', to=settings.AUTH_USER_MODEL),
        ),
    ]