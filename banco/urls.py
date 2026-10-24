from django.urls import path
from . import views

urlpatterns = [
    path('', views.BancoListView.as_view(), name='banco_list'),
    path('nuevo/', views.BancoCreateView.as_view(), name='banco_create'),
    path('<int:pk>/editar/', views.BancoUpdateView.as_view(), name='banco_update'),
    path('<int:pk>/eliminar/', views.BancoDeleteView.as_view(), name='banco_delete'),
    path('beneficiarios/', views.BenificiarioListView.as_view(), name='benificiario_list'),
    path('beneficiarios/nuevo/', views.BenificiarioCreateView.as_view(), name='benificiario_create'),
    path('beneficiarios/<int:pk>/editar/', views.BenificiarioUpdateView.as_view(), name='benificiario_update'),
    path('beneficiarios/<int:pk>/eliminar/', views.BenificiarioDeleteView.as_view(), name='benificiario_delete'),
    path('envios/', views.EnvioBancoListView.as_view(), name='envio_banco_list'),
    path('envios/nuevo/', views.EnvioBancoCreateView.as_view(), name='envio_banco_create'),
    path('envios/<int:pk>/editar/', views.EnvioBancoUpdateView.as_view(), name='envio_banco_update'),
    path('envios/<int:pk>/eliminar/', views.EnvioBancoDeleteView.as_view(), name='envio_banco_delete'),
    path('envios/<int:pk>/pdf/', views.envio_banco_pdf, name='envio_banco_pdf'),
    path('envios/<int:pk>/download/', views.envio_banco_download, name='envio_banco_download'),
    path('envios/pdf/ultimo/', views.envio_banco_last_pdf, name='envio_banco_last_pdf'),
    path('envios/pdf/', views.envio_banco_list_pdf, name='envio_banco_list_pdf'),
    path('envios/excel/', views.export_envios_banco_excel, name='export_envios_banco_excel'),
    path('api/beneficiario/', views.get_beneficiario_json, name='get_beneficiario_json'),
    path('api/banco/', views.banco_ajax, name='banco_ajax'),
    path('api/benificiario/', views.benificiario_ajax, name='benificiario_ajax'),
]
