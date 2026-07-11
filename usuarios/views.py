from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from datetime import date, timedelta
from polizas.models import Poliza
from clientes.models import Cliente
from siniestros.models import Sinistro
from banco.models import EnvioBanco


@login_required
def dashboard(request):
    # Stats cards
    hoy = date.today()
    hace_un_año = hoy - timedelta(days=365)

    # Polizas por mes (últimos 12 meses)
    polizas_mensual = (
        Poliza.objects.filter(fecha_hoy__gte=hace_un_año)
        .annotate(mes=TruncMonth('fecha_hoy'))
        .values('mes')
        .annotate(total=Count('recu'), ingreso=Sum('totale'))
        .order_by('mes')
    )
    meses_labels = []
    polizas_data = []
    ingresos_data = []
    for p in polizas_mensual:
        meses_labels.append(p['mes'].strftime('%b %y') if p['mes'] else '')
        polizas_data.append(p['total'])
        ingresos_data.append(float(p['ingreso'] or 0))

    # Polizas por tipo
    tipos = Poliza.objects.values('letype').annotate(total=Count('recu')).order_by('-total')
    tipos_labels = []
    tipos_data = []
    tipos_colors = []
    color_palette = ['#667eea', '#764ba2', '#11998e', '#38ef7d', '#f093fb',
                     '#f5576c', '#4facfe', '#00f2fe', '#f0006b', '#ffd700']
    for i, t in enumerate(tipos):
        tipos_labels.append(t['letype'] or 'Sin tipo')
        tipos_data.append(t['total'])
        tipos_colors.append(color_palette[i % len(color_palette)])

    # Siniestros por mes (últimos 12 meses)
    siniestros_mensual = (
        Sinistro.objects.filter(date_sinistre__gte=hace_un_año)
        .annotate(mes=TruncMonth('date_sinistre'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    siniestros_data = []
    siniestros_labels = []
    for s in siniestros_mensual:
        siniestros_labels.append(s['mes'].strftime('%b %y') if s['mes'] else '')
        siniestros_data.append(s['total'])

    # Balance pendiente total
    balance_pendiente = Poliza.objects.aggregate(total=Sum('reste'))['total'] or 0

    context = {
        'total_polizas': Poliza.objects.count(),
        'total_clientes': Cliente.objects.count(),
        'total_siniestros': Sinistro.objects.count(),
        'total_envios': EnvioBanco.objects.count(),
        'ultimas_polizas': Poliza.objects.order_by('-recu')[:10],
        'ultimos_siniestros': Sinistro.objects.order_by('-id')[:10],
        'balance_pendiente': float(balance_pendiente),
        # Chart data as JSON
        'meses_labels': meses_labels,
        'polizas_data': polizas_data,
        'ingresos_data': ingresos_data,
        'tipos_labels': tipos_labels,
        'tipos_data': tipos_data,
        'tipos_colors': tipos_colors,
        'siniestros_labels': siniestros_labels,
        'siniestros_data': siniestros_data,
    }
    return render(request, 'dashboard.html', context)
