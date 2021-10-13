from django.urls import path

from registration.views import cambiar_password as c
from .views import *

app_name = 'socio'

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('solicitudcreditocreate/', SolicitudCreditoCreate.as_view(), name='solicitudcreditocreate'),
    path('solicitudcreditodetail/<int:pk>/', SolicitudCreditoDetailView.as_view(), name='solicitudcreditodetail'),
    path('cuotalist/', cuota_list, name='cuotalist'),
    path('rubrolist/', rubro_list, name='rubrolist'),
    path('usuarioupdate/<int:pk>/', SocioUpdate.as_view(),
         name="usuarioupdate"),
    path('cambiarpassword/', c, name='cambiarpassword')

]
