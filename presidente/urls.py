from django.urls import path
from .views import *

app_name = 'presidente'

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('solicitudcreditoupdate/<int:pk>/', SolicitudCreditoUpdate.as_view(), name="solicitudcreditoupdate"),
    # path('usuariodetail/<int:pk>/', UsuarioDetailView.as_view(), name="usuariodetail")

]
