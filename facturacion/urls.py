from django.urls import path
from . import views

urlpatterns = [
    path('factura/recibo/<int:pk>/', views.invoice_by_receipt, name='invoice_by_receipt'),
    path('factura/cliente/<int:client_id>/', views.invoice_by_client, name='invoice_by_client'),
    path('factura/recibo/<int:pk>/excel/', views.invoice_by_receipt_excel, name='invoice_by_receipt_excel'),
    path('factura/lista/<int:client_id>/', views.invoice_list_by_client, name='invoice_list_by_client'),
    path('releve/recibo/<int:pk>/', views.statement_by_receipt, name='statement_by_receipt'),
    path('releve/cliente/<int:client_id>/', views.statement_by_client, name='statement_by_client'),
    path('releve/recibo/<int:pk>/excel/', views.statement_by_receipt_excel, name='statement_by_receipt_excel'),
    path('releve/lista/<int:client_id>/', views.statement_list_by_client, name='statement_list_by_client'),
    path('balance-pendiente/', views.balance_pendiente_list, name='balance_pendiente'),
    path('consulta-vencimiento/', views.consulta_vencimiento, name='consulta_vencimiento'),
]
