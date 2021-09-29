from django.db import models


# Create your models here.


class ReporteConfiguracion(models.Model):
    logo = models.ImageField(default='logo_adetups.png', upload_to='reportes/img')
    descripcion = models.CharField(max_length=100, default='')
    nombre = models.CharField(max_length=100)
