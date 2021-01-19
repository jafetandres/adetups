from django.urls import path
from .views import *

app_name = 'sistema'

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('cambiarpassword/', cambiar_password, name='cambiarpassword'),
    path('asistentecreate/', AsistenteCreate.as_view(), name='asistentecreate'),
    path('presidentecreate/', PresidenteCreate.as_view(), name='presidentecreate'),
    path('usuariodetail/<int:pk>/', UsuarioDetailView.as_view(), name="usuariodetail"),
    path('administradorcreate/', AdministradorCreate.as_view(), name='administradorcreate'),
    path('administradorupdate/<int:pk>/', AdministradorUpdate.as_view(), name='administradorupdate'),
    path('presidentecreate/', PresidenteCreate.as_view(), name='presidentecreate'),
    path('asistentecreate/', AsistenteCreate.as_view(), name='asistentecreate'),
    path('sociocreate/', SocioCreate.as_view(), name='sociocreate'),
    path('socioupdate/<int:pk>/', SocioUpdate.as_view(), name='socioupdate'),
    path('usuarioupdate/<int:pk>/', UsuarioUpdate.as_view(), name='usuarioupdate'),
    path('usuariodelete/<int:pk>/', UsuarioDelete.as_view(), name='usuariodelete'),
    path('clasecreditolist/', ClaseCreditoListView.as_view(), name="clasecreditolist"),
    path('clasecreditodetail/<int:pk>/', ClaseCreditoDetailView.as_view(), name="clasecreditodetail"),
    path('clasecreditocreate/', ClaseCreditoCreate.as_view(), name='clasecreditocreate'),
    path('clasecreditoupdate/<int:pk>/', ClaseCreditoUpdate.as_view(), name='clasecreditoupdate'),
    path('clasecreditodelete/<int:pk>/', ClaseCreditoDelete.as_view(), name='clasecreditodelete'),
    path('clasesolicitudlist/', ClaseSolicitudListView.as_view(), name="clasesolicitudlist"),
    path('clasesolicituddetail/<int:pk>/', ClaseSolicitudDetailView.as_view(), name="clasesolicituddetail"),
    path('clasesolicitudcreate/', ClaseSolicitudCreate.as_view(), name='clasesolicitudcreate'),
    path('clasesolicitudupdate/<int:pk>/', ClaseSolicitudUpdate.as_view(), name='clasesolicitudupdate'),
    path('clasesolicituddelete/<int:pk>/', ClaseSolicitudDelete.as_view(), name='clasesolicituddelete'),
    path('restriccionescreditolist/', RestriccionesCreditoListView.as_view(), name="restriccionescreditolist"),
    path('restriccionescreditodetail/<int:pk>/', RestriccionesCreditoDetailView.as_view(),
         name="restriccionescreditodetail"),
    path('restriccionescreditocreate/', RestriccionesCreditoCreate.as_view(), name='restriccionescreditocreate'),
    path('restriccionescreditoupdate/<int:pk>/', RestriccionesCreditoUpdate.as_view(),
         name='restriccionescreditoupdate'),
    path('restriccionescreditodelete/<int:pk>/', RestriccionesCreditoDelete.as_view(),
         name='restriccionescreditodelete'),
    path('parametrolist/', ParametroListView.as_view(), name="parametrolist"),
    path('parametrodetail/<int:pk>/', ParametroDetailView.as_view(),
         name="parametrodetail"),
    path('parametrocreate/', RestriccionesCreditoCreate.as_view(), name='parametrocreate'),
    path('parametroupdate/<int:pk>/', ParametroUpdate.as_view(),
         name='parametroupdate'),
    path('parametrodelete/<int:pk>/', ParametroDelete.as_view(),
         name='parametrodelete'),

]
