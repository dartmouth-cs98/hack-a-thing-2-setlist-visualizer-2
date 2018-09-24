from django.urls import path
from catalog import views


urlpatterns = [
    path('', views.index, name='index'),
    path('tutorial/', views.tutorial, name='tutorial'),
    path('output/', views.output, name='output'),
]
