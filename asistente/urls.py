from django.urls import path
from .views import *

app_name = 'asistente'

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('solicitudcreditoupdate/<int:pk>/', SolicitudCreditoUpdate.as_view(), name="solicitudcreditoupdate"),
    path('solicitudcreditocreate/', SolicitudCreditoCreate.as_view(), name='solicitudcreditocreate'),
    path('usuariodetail/<int:pk>/', UsuarioDetailView.as_view(), name="usuariodetail"),
    path('sociocreate/', SocioCreate.as_view(), name='sociocreate'),
    path('rubrosocio/', cargar_rubros, name='rubrosocio'),
    path('cargarrubros/', cargar_rubros, name='cargarrubros'),
    path('guardarrubros/', guardar_rubros, name='guardarrubros'),

    path('sociolist/', SocioListView.as_view(), name="sociolist"),
    path('sociodetail/<int:pk>/', SocioDetailView.as_view(), name="sociodetail"),

]
