"""adetups URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from core import views as core_views
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', core_views.home, name="home"),
    # Paths de Auth
    path('', include('registration.urls', namespace='registration')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('sistema/', include('sistema.urls', namespace='sistema')),
    path('socio/', include('socio.urls', namespace='socio')),
    path('asistente/', include('asistente.urls', namespace='asistente')),
    path('presidente/', include('presidente.urls', namespace='presidente')),
    path('resportes/',include('reportes.urls',namespace='reportes'))
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
