from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from usuarios.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', dashboard, name='dashboard'),
    path('clientes/', include('clientes.urls')),
    path('polizas/', include('polizas.urls')),
    path('siniestros/', include('siniestros.urls')),
    path('banco/', include('banco.urls')),
    path('courrier/', include('courrier.urls')),
    path('expertos/', include('expertos.urls')),
    path('garantias/', include('garantias.urls')),
    path('attestations/', include('attestations.urls')),
    path('documentos/', include('documentos.urls')),
    path('core/', include('core.urls')),
    path('facturacion/', include('facturacion.urls')),
    path('audit/', include('audit.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
