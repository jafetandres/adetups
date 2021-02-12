from django.urls import path
from .views import *

app_name = 'socio'

urlpatterns = [
    # path('', index, name="index"),
    path('', HomePageView.as_view(), name="home"),
    # path('clascredetail/<int:pk>/', AdtclascreDetailView.as_view(), name="clascredetail"),
    path('solicitudcreditocreate/', SolicitudCreditoCreate.as_view(), name='solicitudcreditocreate'),
    path('solicitudcreditodetail/<int:pk>/', SolicitudCreditoDetailView.as_view(), name='solicitudcreditodetail'),
    path('cuotalist/', cuota_list, name='cuotalist'),
    path('rubrolist/', rubro_list, name='rubrolist'),
    path('usuarioupdate/<int:pk>/', UsuarioUpdate.as_view(),
         name="usuarioupdate"),
    path('cambiarpassword/', cambiar_password, name='cambiarpassword'),

    # path('clascreupdate/<int:pk>/', AdtclascreUpdate.as_view(), name='clascreupdate'),
    # path('clascredelete/<int:pk>/', AdtclascreDelete.as_view(), name='clascredelete'),

]
