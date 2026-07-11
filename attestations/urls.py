from django.urls import path
from . import views

urlpatterns = [
    path('', views.AttestationListView.as_view(), name='attestation_list'),
    path('importar/', views.import_attestations_excel, name='import_attestations_excel'),
    path('editar/<int:pk>/', views.AttestationUpdateView.as_view(), name='attestation_update'),
    path('eliminar/', views.attestation_delete, name='attestation_delete'),
]
