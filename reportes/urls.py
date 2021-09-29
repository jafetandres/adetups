from django.urls import path
from .views import *

app_name = 'reportes'

urlpatterns = [
    path('reportesolicitudcredito/<int:id>/', generar_reporte_solicitudcredito, name="reportesolicitudcredito"),
]
