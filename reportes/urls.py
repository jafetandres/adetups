from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import *

app_name = 'reportes'

urlpatterns = [
    path('reportesolicitudcredito/<int:id>/', login_required(generar_reporte_solicitudcredito),
         name="reportesolicitudcredito"),
]
