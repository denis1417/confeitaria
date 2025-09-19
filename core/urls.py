from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Colaboradores
    path('colaboradores/', views.colaboradores_list, name='colaboradores_list'),
    path('colaboradores/novo/', views.colaboradores_create,
         name='colaboradores_create'),
    path('colaboradores/editar/<int:id>/',
         views.colaboradores_edit, name='colaboradores_edit'),
    path('colaboradores/deletar/<int:id>/',
         views.colaboradores_delete, name='colaboradores_delete'),

    # Insumos
    path('insumos/', views.insumos_list, name='insumos_list'),
    path('insumos/novo/', views.insumos_create, name='insumos_create'),
    path('insumos/editar/<int:id>/', views.insumos_edit, name='insumos_edit'),
    path('insumos/deletar/<int:id>/', views.insumos_delete, name='insumos_delete'),

    # Produtos Prontos
    path('produtos/', views.produtos_list, name='produtos_list'),
    path('produtos/novo/', views.produtos_create, name='produtos_create'),
    path('produtos/editar/<int:id>/', views.produtos_edit, name='produtos_edit'),
    path('produtos/deletar/<int:id>/',
         views.produtos_delete, name='produtos_delete'),

    # Saída de Insumos
    path('saidas/', views.saida_insumo_list, name='saida_insumo_list'),
    path('saidas/novo/', views.saida_insumo_create, name='saida_insumo_create'),
    path('saidas/<int:id>/deletar/', views.saida_insumo_delete,
         name='saida_insumo_delete'),

    # Criar Usuário
    path('criar-usuario/', views.criar_usuario, name='criar_usuario'),

    # Usuários
    path('usuarios/', views.listar_usuarios,
         name='listar_usuarios'),  # lista de usuários
    path('usuarios/deletar/<int:id>/', views.usuario_delete,
         name='usuario_delete'),  # deletar usuário
    path('usuarios/<int:id>/editar/', views.usuario_edit,
         name='usuario_edit'),  # editar usuário

    # Logout
    path('logout/', views.logout_view, name='logout'),
]
