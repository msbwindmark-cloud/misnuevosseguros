from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm
from io import BytesIO
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl import Workbook
from .models import Banco, Benificiario, EnvioBanco
from .forms import BancoForm, BenificiarioForm, EnvioBancoForm


class BancoListView(ListView):
    model = Banco
    template_name = 'banco/lista.html'
    context_object_name = 'bancos'


class BenificiarioListView(ListView):
    model = Benificiario
    template_name = 'banco/beneficiarios.html'
    context_object_name = 'beneficiarios'


class EnvioBancoListView(ListView):
    model = EnvioBanco
    template_name = 'banco/envios.html'
    context_object_name = 'envios'


@method_decorator(staff_member_required, name='dispatch')
class BancoCreateView(CreateView):
    model = Banco
    form_class = BancoForm
    template_name = 'banco/banco_form.html'
    success_url = reverse_lazy('banco_list')


@method_decorator(staff_member_required, name='dispatch')
class BancoUpdateView(UpdateView):
    model = Banco
    form_class = BancoForm
    template_name = 'banco/banco_form.html'
    success_url = reverse_lazy('banco_list')


@method_decorator(staff_member_required, name='dispatch')
class BancoDeleteView(DeleteView):
    model = Banco
    template_name = 'banco/banco_confirm_delete.html'
    success_url = reverse_lazy('banco_list')


@method_decorator(staff_member_required, name='dispatch')
class BenificiarioCreateView(CreateView):
    model = Benificiario
    form_class = BenificiarioForm
    template_name = 'banco/beneficiario_form.html'
    success_url = reverse_lazy('benificiario_list')


@method_decorator(staff_member_required, name='dispatch')
class BenificiarioUpdateView(UpdateView):
    model = Benificiario
    form_class = BenificiarioForm
    template_name = 'banco/beneficiario_form.html'
    success_url = reverse_lazy('benificiario_list')


@method_decorator(staff_member_required, name='dispatch')
class BenificiarioDeleteView(DeleteView):
    model = Benificiario
    template_name = 'banco/beneficiario_confirm_delete.html'
    success_url = reverse_lazy('benificiario_list')


@method_decorator(staff_member_required, name='dispatch')
class EnvioBancoCreateView(CreateView):
    model = EnvioBanco
    form_class = EnvioBancoForm
    template_name = 'banco/envio_form.html'
    success_url = reverse_lazy('envio_banco_list')


@method_decorator(staff_member_required, name='dispatch')
class EnvioBancoUpdateView(UpdateView):
    model = EnvioBanco
    form_class = EnvioBancoForm
    template_name = 'banco/envio_form.html'
    success_url = reverse_lazy('envio_banco_list')


@method_decorator(staff_member_required, name='dispatch')
class EnvioBancoDeleteView(DeleteView):
    model = EnvioBanco
    template_name = 'banco/envio_confirm_delete.html'
    success_url = reverse_lazy('envio_banco_list')


@staff_member_required
def envio_banco_pdf(request, pk):
    try:
        envio = EnvioBanco.objects.get(pk=pk)
    except EnvioBanco.DoesNotExist:
        return HttpResponse('Envío no encontrado', status=404)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], textColor=colors.HexColor('#4e73df'))
    elements.append(Paragraph(f'Envío Bancario nº {envio.id}', title_style))
    elements.append(Spacer(1, 0.5*cm))
    data = [
        ['Campo', 'Valor'],
        ['Nombre', envio.nom_envoie],
        ['Banco', envio.banque_envoie],
        ['Cuenta', envio.compte_envoie],
        ['Fecha de envío', envio.date_envoie.strftime('%d/%m/%Y') if envio.date_envoie else ''],
        ['Monto', f'{envio.montant_envoie} MAD'],
        ['Motivo', envio.motif_envoie],
        ['Beneficiario', str(envio.benificiario)],
        ['Banco', str(envio.banco)],
    ]
    table = Table(data, colWidths=[5*cm, 10*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4e73df')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f8f9fc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', headers={
        'Content-Disposition': f'attachment; filename="envio_{envio.id}.pdf"'
    })


@staff_member_required
def envio_banco_list_pdf(request):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph('Lista de Envíos Bancarios', styles['Title']))
    elements.append(Spacer(1, 0.5*cm))
    data = [['ID', 'Nombre', 'Banco', 'Cuenta', 'Fecha', 'Monto', 'Beneficiario']]
    for e in EnvioBanco.objects.all():
        fecha = e.date_envoie.strftime('%d/%m/%Y') if e.date_envoie else ''
        data.append([str(e.id), e.nom_envoie, e.banque_envoie, e.compte_envoie, fecha, str(e.montant_envoie), str(e.benificiario)])
    table = Table(data, colWidths=[1.5*cm, 3*cm, 3*cm, 3*cm, 2.5*cm, 2.5*cm, 3.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4e73df')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fc')]),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', headers={
        'Content-Disposition': 'attachment; filename="envios_bancarios.pdf"'
    })


@staff_member_required
def export_envios_banco_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Envíos Bancarios'
    headers = ['ID', 'Nombre', 'Banco', 'Cuenta', 'Fecha', 'Monto', 'Motivo', 'Beneficiario', 'Banco (FK)', 'Creado']
    header_fill = PatternFill(start_color='0D6EFD', end_color='0D6EFD', fill_type='solid')
    header_font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=col, value=h)
        c.font = header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal='center')
    for row, e in enumerate(EnvioBanco.objects.all().order_by('-id'), 2):
        ws.cell(row=row, column=1, value=e.id)
        ws.cell(row=row, column=2, value=e.nom_envoie)
        ws.cell(row=row, column=3, value=e.banque_envoie)
        ws.cell(row=row, column=4, value=e.compte_envoie)
        ws.cell(row=row, column=5, value=e.date_envoie.strftime('%d/%m/%Y') if e.date_envoie else '')
        ws.cell(row=row, column=6, value=float(e.montant_envoie))
        ws.cell(row=row, column=7, value=e.motif_envoie)
        ws.cell(row=row, column=8, value=str(e.benificiario))
        ws.cell(row=row, column=9, value=str(e.banco))
        ws.cell(row=row, column=10, value=e.creado_el.strftime('%d/%m/%Y %H:%M') if e.creado_el else '')
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 22
    ws.column_dimensions['E'].width = 14
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 30
    ws.column_dimensions['H'].width = 25
    ws.column_dimensions['I'].width = 20
    ws.column_dimensions['J'].width = 18
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="envios_bancarios.xlsx"'
    wb.save(response)
    return response
