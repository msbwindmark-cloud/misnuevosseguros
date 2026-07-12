import json
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from swagger_schema import manual_paths


@staff_member_required
def swagger_api_schema(request):
    schema = {
        'openapi': '3.0.0',
        'info': {
            'title': 'Proyecto SIS API',
            'version': 'v1',
            'description': 'Documentación de la API del Proyecto SIS - Sistema de Seguros',
        },
        'paths': manual_paths,
        'tags': [
            {'name': 'Pólizas API', 'description': 'Endpoints de gestión de pólizas'},
            {'name': 'Siniestros API', 'description': 'Endpoints de gestión de siniestros'},
            {'name': 'Siniestros', 'description': 'Generación de PDF/Excel de siniestros'},
            {'name': 'Clientes API', 'description': 'Gestión y borrado de clientes'},
            {'name': 'Ofertas API', 'description': 'Ofertas / presupuestos de seguros'},
            {'name': 'Documentos API', 'description': 'Gestión de documentos adjuntos'},
            {'name': 'Core API', 'description': 'Endpoints utilitarios (salat, expiring, etc.)'},
            {'name': 'Exportaciones', 'description': 'Generación de PDF y Excel'},
            {'name': 'Facturación', 'description': 'Facturas, relevés y balances'},
            {'name': 'Auditoría', 'description': 'Log de auditoría del sistema'},
        ],
    }
    return HttpResponse(
        json.dumps(schema, indent=2, ensure_ascii=False),
        content_type='application/json',
    )


@staff_member_required
def swagger_ui_view(request):
    return render(request, 'swagger_ui.html')
