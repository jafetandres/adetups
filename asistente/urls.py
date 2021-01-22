from django.urls import path, re_path
from .views import *

app_name = 'asistente'

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('solicitudcreditoupdate/<int:pk>/', SolicitudCreditoUpdate.as_view(), name="solicitudcreditoupdate"),
    re_path('solicitudcreditocreate/(?P<usuario_id>\d+)/$', SolicitudCreditoCreate.as_view(),
         name='solicitudcreditocreate'),
    # path('solicitudcreditocreate/<int:socio_id>/', SolicitudCreditoCreate.as_view(),
    #      name='solicitudcreditocreate'),
    path('usuariodetail/<int:pk>/', UsuarioDetailView.as_view(), name="usuariodetail"),
    path('sociocreate/', SocioCreate.as_view(), name='sociocreate'),
    path('rubrosocio/', cargar_rubros, name='rubrosocio'),
    path('cargarrubros/', cargar_rubros, name='cargarrubros'),
    path('guardarrubros/', guardar_rubros, name='guardarrubros'),
    path('escogersocio/', escoger_socio, name='escogersocio'),
    path('sociolist/', SocioListView.as_view(), name="sociolist"),
    path('sociodetail/<int:pk>/', SocioDetailView.as_view(), name="sociodetail"),

]
