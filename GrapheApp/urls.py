from django.urls import path
from .views import file, graphe

urlpatterns = [
    path('', file, name='home'),
    path('graphe/', graphe, name='graphe'),
  
]
