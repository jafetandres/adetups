from django.urls import path
from .views import *

app_name = 'presidente'

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('solicitudcreditoupdate/<int:pk>/', SolicitudCreditoUpdate.as_view(), name="solicitudcreditoupdate"),
    path('solicitudcreditolist/', SolicitudCreditoList.as_view(), name="solicitudcreditolist"),

    path('sociolist/', SocioListView.as_view(), name="sociolist"),
    path('sociodetail/<int:pk>/', SocioDetailView.as_view(), name="sociodetail"),
    path('sociodelete/<int:pk>/', SocioDelete.as_view(), name="sociodelete"),

    path('usuarioupdate/<int:pk>/', UsuarioUpdate.as_view(),
         name="usuarioupdate"),
    path('cambiarpassword/', cambiar_password, name='cambiarpassword'),
    path('consultarrubros/', consultar_rubros, name="consultar_rubros"),
    path('clasecreditolist/', ClaseCreditoListView.as_view(), name="clasecreditolist"),
    path('clasecreditodetail/<int:pk>/', ClaseCreditoDetailView.as_view(), name="clasecreditodetail"),
    path('clasecreditocreate/', ClaseCreditoCreate.as_view(), name='clasecreditocreate'),
    path('clasecreditoupdate/<int:pk>/', ClaseCreditoUpdate.as_view(), name='clasecreditoupdate'),
    path('clasecreditodelete/<int:pk>/', ClaseCreditoDelete.as_view(), name='clasecreditodelete'),
    path('restriccionclasecreditolist/', RestriccionClaseCreditoListView.as_view(), name="restriccionclasecreditolist"),
    path('restriccionclasecreditocreate/', RestriccionClaseCreditoCreate.as_view(),
         name="restriccionclasecreditocreate"),
    path('restriccionclasecreditoupdate/<int:pk>/', RestriccionClaseCreditoUpdate.as_view(),
         name='restriccionclasecreditoupdate'),
    path('restriccionclasecreditodelete/<int:pk>/', RestriccionClaseCreditoDelete.as_view(),
         name='restriccionclasecreditodelete'),
    path('rubrolist/', RubroListView.as_view(), name="rubrolist"),

    path('rubrodetail/<int:pk>/', RubroDetailView.as_view(),
         name="rubrodetail"),
    path('rubrocreate/', RubroCreate.as_view(), name="rubrocreate"),
    path('rubroupdate/<int:pk>/', RubroUpdate.as_view(),
         name="rubroupdate"),
    path('rubrodelete/<int:pk>/', RubroDelete.as_view(),
         name="rubrodelete"),
    path('creditolist/', CreditoListView.as_view(), name="creditolist"),
    path('creditodetail/<int:pk>/', CreditoDetail.as_view(), name="creditodetail"),
    path('liquidacioncreditocreate/<int:credito_id>/', LicquidacionCreditoCreate.as_view(),
         name="liquidacioncreditocreate"),
    path('reportecredito', resultadoTest, name="reportecredito")

]
