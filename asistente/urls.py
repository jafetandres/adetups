from django.urls import path, re_path
from .views import *

app_name = 'asistente'

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('escogerarchivo', EscogerArchivoPageView.as_view(), name="escogerarchivo"),
    path('solicitudcreditoupdate/<int:pk>/', SolicitudCreditoUpdate.as_view(), name="solicitudcreditoupdate"),
    re_path('solicitudcreditocreate/(?P<usuario_id>\d+)/$', SolicitudCreditoCreate.as_view(),
            name='solicitudcreditocreate'),
    # path('solicitudcreditocreate/<int:socio_id>/', SolicitudCreditoCreate.as_view(),
    #      name='solicitudcreditocreate'),

    path('sociocreate/', SocioCreate.as_view(), name='sociocreate'),
    path('cargarrubrosmoviestar/', cargar_rubros_moviestar, name='cargarrubrosmoviestar'),
    path('cargarrubrosgeneral/', cargar_rubros_general, name='cargarrubrosgeneral'),
    path('cambiarpassword/', cambiar_password, name='cambiarpassword'),
    path('guardarrubrosmoviestar/', guardar_rubros_moviestar, name='guardarrubrosmoviestar'),
    path('guardarrubrosgeneral/', guardar_rubros_general, name='guardarrubrosgeneral'),
    path('escogersocio/', escoger_socio, name='escogersocio'),
    path('sociolist/', SocioListView.as_view(), name="sociolist"),
    path('sociodetail/<int:pk>/', SocioDetailView.as_view(), name="sociodetail"),
    path('clasecreditolist/', ClaseCreditoListView.as_view(), name="clasecreditolist"),
    path('clasecreditodetail/<int:pk>/', ClaseCreditoDetailView.as_view(), name="clasecreditodetail"),
    path('parametrolist/', ParametroListView.as_view(), name="parametrolist"),
    path('parametrodetail/<int:pk>/', ParametroDetailView.as_view(),
         name="parametrodetail"),
    path('rubrolist/', RubroListView.as_view(), name="rubrolist"),

    path('rubrodetail/<int:pk>/', RubroDetailView.as_view(),
         name="rubrodetail"),
    path('rubrocreate/', RubroCreate.as_view(), name="rubrocreate"),
    path('rubroupdate/<int:pk>/', RubroUpdate.as_view(),
         name="rubroupdate"),
    path('rubrodelete/<int:pk>/', RubroDelete.as_view(),
         name="rubrodelete"),
    path('consultarrubros/', consultar_rubros, name="consultar_rubros"),
    path('rubrosociocreate/', RubroSocioCreate.as_view(), name="rubrosociocreate"),
    path('rubrosociodelete/<int:pk>/', RubroSocioDelete.as_view(),
         name="rubrosociodelete"),
    path('usuarioupdate/<int:pk>/', UsuarioUpdate.as_view(),
         name="usuarioupdate"),
    path('creditolist/', CreditoListView.as_view(), name="creditolist"),
    path('creditodetail/<int:pk>/', CreditoDetail.as_view(), name="creditodetail"),
    path('liquidacioncreditocreate/<int:credito_id>/', LicquidacionCreditoCreate.as_view(),
         name="liquidacioncreditocreate"),
    path('consultarcuotas/', consultar_cuotas, name="consultarcuotas"),
    path('restriccionclasecreditolist/', RestriccionClaseCreditoList.as_view(), name="restriccionclasecreditolist")

]
