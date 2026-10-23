from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

# Cada endereço aponta para uma view. O name permite montar o endereço com
# reverse() e {% url %}, sem escrevê-lo à mão em vários lugares.
urlpatterns = [
    path('', views.mural, name='mural'),
    path('recado/<int:id>/', views.recado, name='recado'),
    path('recado/<int:id>/arquivar/', views.arquivar, name='arquivar'),
    path('sobre/', views.sobre, name='sobre'),
    path('entrar/', views.Entrar.as_view(), name='entrar'),
    # A LogoutView do Django só aceita POST e volta para LOGOUT_REDIRECT_URL.
    path('sair/', LogoutView.as_view(), name='sair'),
    path('cadastro/', views.cadastro, name='cadastro'),
]
