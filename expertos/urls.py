from django.urls import path
from . import views

urlpatterns = [
    path('', views.ExpertoListView.as_view(), name='experto_list'),
    path('nuevo/', views.ExpertoCreateView.as_view(), name='experto_create'),
    path('editar/<int:pk>/', views.ExpertoUpdateView.as_view(), name='experto_update'),
    path('eliminar/<int:pk>/', views.ExpertoDeleteView.as_view(), name='experto_delete'),
]
