from django.urls import path
from . import views

urlpatterns = [
    path('', views.EnvioCourrierListView.as_view(), name='courrier_list'),
    path('nuevo/', views.EnvioCourrierCreateView.as_view(), name='courrier_create'),
    path('<int:pk>/editar/', views.EnvioCourrierUpdateView.as_view(), name='courrier_update'),
    path('<int:pk>/eliminar/', views.EnvioCourrierDeleteView.as_view(), name='courrier_delete'),
    path('<int:pk>/pdf/', views.envio_courrier_pdf, name='courrier_pdf'),
    path('pdf/', views.envio_courrier_list_pdf, name='courrier_list_pdf'),
    path('excel/', views.export_envios_courrier_excel, name='export_envios_courrier_excel'),
    path('destinataires/', views.DestinataireListView.as_view(), name='destinataire_list'),
    path('destinataires/nuevo/', views.DestinataireCreateView.as_view(), name='destinataire_create'),
    path('destinataires/<int:pk>/editar/', views.DestinataireUpdateView.as_view(), name='destinataire_update'),
    path('destinataires/<int:pk>/eliminar/', views.DestinataireDeleteView.as_view(), name='destinataire_delete'),
    path('expediteurs/', views.ExpediteurListView.as_view(), name='expediteur_list'),
    path('expediteurs/nuevo/', views.ExpediteurCreateView.as_view(), name='expediteur_create'),
    path('expediteurs/<int:pk>/editar/', views.ExpediteurUpdateView.as_view(), name='expediteur_update'),
    path('expediteurs/<int:pk>/eliminar/', views.ExpediteurDeleteView.as_view(), name='expediteur_delete'),
]
