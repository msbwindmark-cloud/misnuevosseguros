from django.urls import path
from . import views

urlpatterns = [
    path('tipos/', views.TipoDocumentoListView.as_view(), name='tipo_documento_list'),
    path('tipos/nuevo/', views.TipoDocumentoCreateView.as_view(), name='tipo_documento_create'),
    path('tipos/<int:pk>/editar/', views.TipoDocumentoUpdateView.as_view(), name='tipo_documento_update'),
    path('tipos/<int:pk>/eliminar/', views.TipoDocumentoDeleteView.as_view(), name='tipo_documento_delete'),
    path('add-docs/', views.add_document_to_poliza, name='add_document_to_poliza'),
    path('add-docs/<int:recu>/', views.add_document_to_poliza, name='add_document_to_poliza'),
    path('por-cliente/', views.consulter_documents_des_clients, name='consulter_documents_des_clients'),
]
