from django.urls import path
from . import views

urlpatterns = [
    path('', views.PolizaListView.as_view(), name='poliza_list'),
    path('nueva/', views.PolizaCreateView.as_view(), name='poliza_create'),
    path('<int:pk>/', views.PolizaDetailView.as_view(), name='poliza_detail'),
    path('<int:pk>/editar/', views.PolizaUpdateView.as_view(), name='poliza_update'),
    path('api/garantia/<int:pk>/options/', views.get_garantia_options, name='get_garantia_options'),
    path('api/option/<int:pk>/franchises/', views.get_option_franchises, name='get_option_franchises'),
    path('api/clientes/', views.get_clientes_json, name='get_clientes_json'),
    path('api/cliente/crear/', views.crear_cliente_ajax, name='crear_cliente_ajax'),
    path('api/<int:pk>/garantias/', views.poliza_garantias_data, name='poliza_garantias_data'),
    path('api/<int:pk>/documentos/', views.poliza_documents_data, name='poliza_documents_data'),
    path('<int:pk>/docs/agregar/', views.poliza_documentos_agregar, name='poliza_documentos_agregar'),
    path('api/attestations/', views.get_attestations_json, name='get_attestations_json'),
    path('api/attestation/next/', views.get_next_attestation, name='get_next_attestation'),
    path('api/attestation/creer/', views.crear_attestation_ajax, name='crear_attestation_ajax'),
    path('api/polizas/', views.get_polizas_json, name='get_polizas_json'),
    path('api/docs-by-police/', views.poliza_docs_by_police, name='poliza_docs_by_police'),
    path('api/datatables/', views.poliza_datatables_data, name='poliza_datatables_data'),
]
