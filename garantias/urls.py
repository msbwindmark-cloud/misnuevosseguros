from django.urls import path
from . import views

urlpatterns = [
    path('', views.GarantiaListView.as_view(), name='garantia_list'),
    path('nueva/', views.GarantiaCreateView.as_view(), name='garantia_create'),
    path('<int:pk>/editar/', views.GarantiaUpdateView.as_view(), name='garantia_update'),
    path('<int:pk>/eliminar/', views.GarantiaDeleteView.as_view(), name='garantia_delete'),
]
