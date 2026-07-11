from django.urls import path
from . import views

urlpatterns = [
    path('', views.SinistroListView.as_view(), name='sinistro_list'),
    path('nuevo/', views.SinistroCreateView.as_view(), name='sinistro_create'),
    path('<int:pk>/editar/', views.SinistroUpdateView.as_view(), name='sinistro_update'),
    path('<int:pk>/eliminar/', views.sinistro_delete, name='sinistro_delete'),
    path('eliminar-multiple/', views.sinistro_bulk_delete, name='sinistro_bulk_delete'),
    path('<int:pk>/pdf/', views.sinistro_pdf, name='sinistro_pdf'),
    path('pdf/', views.sinistro_list_pdf, name='sinistro_list_pdf'),
    path('excel/', views.sinistro_list_excel, name='sinistro_list_excel'),
    path('api/polizas/', views.get_polizas_json, name='get_polizas_siniestro'),
    path('api/poliza/<int:pk>/documentos/', views.get_poliza_documentos, name='get_poliza_documentos'),
    path('api/<int:pk>/documentos/', views.sinistro_documentos_data, name='sinistro_documentos_data'),
    path('<int:pk>/docs/agregar/', views.sinistro_documentos_agregar, name='sinistro_documentos_agregar'),
]
