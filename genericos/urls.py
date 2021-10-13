from django.urls import path, re_path
from .views import *

app_name = 'genericos'

urlpatterns = [
    path('table/as_json/<str:app>', TableAsJSON.as_view(), name='table-as-json'),
]
