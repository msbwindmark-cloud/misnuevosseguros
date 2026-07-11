from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .models import EnvioCourrier, Destinataire, Expediteur
from .forms import DestinataireForm, ExpediteurForm, EnvioCourrierForm
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm
from io import BytesIO
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl import Workbook

# --- Destinataire CRUD ---
@method_decorator(staff_member_required, name='dispatch')
class DestinataireListView(ListView):
    model = Destinataire
    template_name = 'courrier/destinataire_list.html'
    context_object_name = 'destinataires'

@method_decorator(staff_member_required, name='dispatch')
class DestinataireCreateView(CreateView):
    model = Destinataire
    form_class = DestinataireForm
    template_name = 'courrier/destinataire_form.html'
    success_url = reverse_lazy('destinataire_list')

@method_decorator(staff_member_required, name='dispatch')
class DestinataireUpdateView(UpdateView):
    model = Destinataire
    form_class = DestinataireForm
    template_name = 'courrier/destinataire_form.html'
    success_url = reverse_lazy('destinataire_list')

@method_decorator(staff_member_required, name='dispatch')
class DestinataireDeleteView(DeleteView):
    model = Destinataire
    template_name = 'courrier/destinataire_confirm_delete.html'
    success_url = reverse_lazy('destinataire_list')

# --- Expediteur CRUD ---
@method_decorator(staff_member_required, name='dispatch')
class ExpediteurListView(ListView):
    model = Expediteur
    template_name = 'courrier/expediteur_list.html'
    context_object_name = 'expediteurs'

@method_decorator(staff_member_required, name='dispatch')
class ExpediteurCreateView(CreateView):
    model = Expediteur
    form_class = ExpediteurForm
    template_name = 'courrier/expediteur_form.html'
    success_url = reverse_lazy('expediteur_list')

@method_decorator(staff_member_required, name='dispatch')
class ExpediteurUpdateView(UpdateView):
    model = Expediteur
    form_class = ExpediteurForm
    template_name = 'courrier/expediteur_form.html'
    success_url = reverse_lazy('expediteur_list')

@method_decorator(staff_member_required, name='dispatch')
class ExpediteurDeleteView(DeleteView):
    model = Expediteur
    template_name = 'courrier/expediteur_confirm_delete.html'
    success_url = reverse_lazy('expediteur_list')

# --- EnvioCourrier CRUD ---
class EnvioCourrierListView(ListView):
    model = EnvioCourrier
    template_name = 'courrier/lista.html'
    context_object_name = 'envios'

@method_decorator(staff_member_required, name='dispatch')
class EnvioCourrierCreateView(CreateView):
    model = EnvioCourrier
    form_class = EnvioCourrierForm
    template_name = 'courrier/envio_form.html'
    success_url = reverse_lazy('courrier_list')

@method_decorator(staff_member_required, name='dispatch')
class EnvioCourrierUpdateView(UpdateView):
    model = EnvioCourrier
    form_class = EnvioCourrierForm
    template_name = 'courrier/envio_form.html'
    success_url = reverse_lazy('courrier_list')

@method_decorator(staff_member_required, name='dispatch')
class EnvioCourrierDeleteView(DeleteView):
    model = EnvioCourrier
    template_name = 'courrier/envio_confirm_delete.html'
    success_url = reverse_lazy('courrier_list')

@staff_member_required
def envio_courrier_pdf(request, pk):
    from .models import EnvioCourrier
    envio = EnvioCourrier.objects.get(pk=pk)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph(f'Envio de Courrier n° {envio.id}', styles['Title']))
    elements.append(Spacer(1, 0.5*cm))
    data = [
        ['Campo', 'Valor'],
        ['Fecha', envio.date_envoie_courrier.strftime('%d/%m/%Y') if envio.date_envoie_courrier else ''],
        ['Expediteur', envio.expediteur_envoie_courrier],
        ['Destinataire', envio.destinataire_envoie_courrier],
        ['Adresse', envio.addresse_envoie_courrier],
    ]
    table = Table(data, colWidths=[5*cm, 10*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4e73df')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BACKGROUND', (0,1), (0,-1), colors.HexColor('#f8f9fc')),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', headers={
        'Content-Disposition': f'attachment; filename="courrier_{pk}.pdf"'
    })

@staff_member_required
def envio_courrier_list_pdf(request):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph('Lista de Envios de Courrier', styles['Title']))
    elements.append(Spacer(1, 0.5*cm))
    data = [['ID', 'Fecha', 'Expediteur', 'Destinataire', 'Adresse']]
    for e in EnvioCourrier.objects.all().order_by('-id'):
        data.append([
            str(e.id),
            e.date_envoie_courrier.strftime('%d/%m/%Y') if e.date_envoie_courrier else '',
            e.expediteur_envoie_courrier,
            e.destinataire_envoie_courrier,
            e.addresse_envoie_courrier,
        ])
    table = Table(data, colWidths=[2*cm, 2.5*cm, 4*cm, 4*cm, 5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4e73df')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', headers={
        'Content-Disposition': 'attachment; filename="lista_courrier.pdf"'
    })


@staff_member_required
def export_envios_courrier_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Envíos Courrier'
    headers = ['ID', 'Fecha', 'Remitente', 'Destinatario', 'Dirección', 'Tipo Doc', 'Nombre Doc', 'Tamaño', 'Creado']
    header_fill = PatternFill(start_color='198754', end_color='198754', fill_type='solid')
    header_font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=col, value=h)
        c.font = header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal='center')
    for row, e in enumerate(EnvioCourrier.objects.all().order_by('-id'), 2):
        ws.cell(row=row, column=1, value=e.id)
        ws.cell(row=row, column=2, value=e.date_envoie_courrier.strftime('%d/%m/%Y') if e.date_envoie_courrier else '')
        ws.cell(row=row, column=3, value=e.expediteur_envoie_courrier)
        ws.cell(row=row, column=4, value=e.destinataire_envoie_courrier)
        ws.cell(row=row, column=5, value=e.addresse_envoie_courrier)
        ws.cell(row=row, column=6, value=e.tipo_documento_envoie_courrier or '')
        ws.cell(row=row, column=7, value=e.nombre_documento_envoie_courrier or '')
        ws.cell(row=row, column=8, value=e.tamanio_documento_envoie_courrier or '')
        ws.cell(row=row, column=9, value=e.creado_el.strftime('%d/%m/%Y %H:%M') if e.creado_el else '')
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 16
    ws.column_dimensions['C'].width = 25
    ws.column_dimensions['D'].width = 25
    ws.column_dimensions['E'].width = 35
    ws.column_dimensions['F'].width = 15
    ws.column_dimensions['G'].width = 20
    ws.column_dimensions['H'].width = 12
    ws.column_dimensions['I'].width = 18
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="envios_courrier.xlsx"'
    wb.save(response)
    return response
