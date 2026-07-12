from django.urls import path
from . import views

urlpatterns = [
    path('api/tipos-vehiculo/', views.tipo_vehiculo_api, name='tipo_vehiculo_api'),
    path('api/modalidades/', views.modalidad_api, name='modalidad_api'),
    path('api/duraciones/', views.duracion_api, name='duracion_api'),
    path('api/estados/', views.estado_oferta_api, name='estado_oferta_api'),
    path('', views.OfertaListView.as_view(), name='oferta_list'),
    path('nueva/', views.OfertaCreateView.as_view(), name='oferta_create'),
    path('<int:pk>/editar/', views.OfertaUpdateView.as_view(), name='oferta_update'),
    path('<int:pk>/eliminar/', views.OfertaDeleteView.as_view(), name='oferta_delete'),
]
