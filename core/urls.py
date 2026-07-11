from django.urls import path
from . import views

urlpatterns = [
    path('exportar/polizas/pdf/', views.export_polizas_pdf, name='export_polizas_pdf'),
    path('exportar/polizas/excel/', views.export_polizas_excel, name='export_polizas_excel'),
    path('exportar/clientes/excel/', views.export_clientes_excel, name='export_clientes_excel'),
    path('poliza/<int:pk>/pdf/', views.generate_poliza_pdf, name='generate_poliza_pdf'),
    path('poliza/<int:pk>/pdf-sans-entete/', views.generate_poliza_pdf_sans_entete, name='generate_poliza_pdf_sans_entete'),
    path('poliza/<int:pk>/pdf-with-header/', views.generate_poliza_pdf_with_header, name='generate_poliza_pdf_with_header'),
    path('poliza/delete/', views.poliza_list_delete, name='poliza_list_delete'),
    path('exportar/polizas-eliminadas/excel/', views.export_polizas_eliminadas_excel, name='export_polizas_eliminadas_excel'),
    path('exportar/expertos/pdf/', views.export_expertos_pdf, name='export_expertos_pdf'),
    path('exportar/clientes/<int:pk>/pdf/', views.export_cliente_pdf, name='export_cliente_pdf'),
    path('exportar/clientes-eliminados/excel/', views.export_clientes_eliminados_excel, name='export_clientes_eliminados_excel'),
    path('backup/', views.backup_view, name='backup_view'),
    path('check-expiring/', views.check_expiring_ajax, name='check_expiring_ajax'),
    path('escanear-qr/', views.escanear_qr, name='escanear_qr'),
    path('api/ciudades-salat/', views.ciudades_salat_api, name='ciudades_salat_api'),
]
