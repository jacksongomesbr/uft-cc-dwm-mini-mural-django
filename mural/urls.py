from django.urls import path

from . import views

# Cada endereço aponta para uma view. O name permite montar o endereço com
# reverse() e {% url %}, sem escrevê-lo à mão em vários lugares.
urlpatterns = [
    path('', views.mural, name='mural'),
    path('recado/<int:id>/', views.recado, name='recado'),
    path('recado/<int:id>/arquivar/', views.arquivar, name='arquivar'),
    path('sobre/', views.sobre, name='sobre'),
]
