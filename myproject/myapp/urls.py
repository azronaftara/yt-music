from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('fetch_audio/', views.fetch_audio, name='fetch_audio'),
]
