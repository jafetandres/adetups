from django.urls import path

from . import views

app_name = 'registration'
urlpatterns = [
    path('', views.login_view, name='login'),
    path('password_change', views.cambiar_password, name='password_change')
]
