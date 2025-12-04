from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login, name='login'),
    path('adm_inicio/', views.adm_inicio, name='adm_inicio'),
    path('home_page/', views.home_page, name='home_page'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('adm/editar/<int:user_id>/', views.adm_editar_usuario, name='adm_editar_usuario'),
    path('adm/excluir/<int:user_id>/', views.adm_excluir_usuario, name='adm_excluir_usuario'),
]