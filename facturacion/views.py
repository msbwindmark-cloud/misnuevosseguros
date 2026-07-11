import io
from decimal import Decimal
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Sum
from polizas.models import Poliza
from clientes.models import Cliente

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm, cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor, black, white, Color
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.platypus.flowables import HRFlowable
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


COMPANY_NAME = "PROYECTO SIS"
COMPANY_ADDRESS = "123 Rue Example, 75000 Paris"
COMPANY_PHONE = "Tel: +33 1 23 45 67 89"
COMPANY_EMAIL = "info@proyectosis.com"
COMPANY_SIRET = "SIRET: 123 456 789 00012"


def _build_pdf_response(buffer, filename):
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def _header_table(doc_title="FACTURE", doc_number=""):
    data = [
        [Paragraph(f"<b>{COMPANY_NAME}</b>", ParagraphStyle('hdr', fontSize=16, textColor=HexColor('#0d6efd'))),
         Paragraph(f"<b>{doc_title}</b><br/>{doc_number}", ParagraphStyle('hdrr', fontSize=14, alignment=TA_RIGHT))],
        [Paragraph(COMPANY_ADDRESS, ParagraphStyle('addr', fontSize=8)),
         Paragraph("", ParagraphStyle('addr'))],
        [Paragraph(COMPANY_PHONE, ParagraphStyle('addr', fontSize=8)),
         Paragraph("", ParagraphStyle('addr'))],
        [Paragraph(COMPANY_EMAIL, ParagraphStyle('addr', fontSize=8)),
         Paragraph("", ParagraphStyle('addr'))],
    ]
    t = Table(data, colWidths=[A4[0]/2-40, A4[0]/2-40])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('SPAN', (0, 1), (0, 3)),
        ('LINEBELOW', (0, 0), (-1, 0), 1, HexColor('#0d6efd')),
    ]))
    return t


def _client_info_table(poliza):
    data = [
        [Paragraph("<b>CLIENT</b>", ParagraphStyle('clbl', fontSize=10))],
        [Paragraph(f"{poliza.assure} {poliza.prenom}", ParagraphStyle('clv', fontSize=10))],
        [Paragraph(f"Code client: {poliza.code_client}", ParagraphStyle('clv', fontSize=10))],
    ]
    if poliza.address_client:
        data.append([Paragraph(poliza.address_client.replace('\n', '<br/>'), ParagraphStyle('clv', fontSize=10))])
    if poliza.telefono:
        data.append([Paragraph(f"Tel: {poliza.telefono}", ParagraphStyle('clv', fontSize=10))])
    if poliza.email:
        data.append([Paragraph(f"Email: {poliza.email}", ParagraphStyle('clv', fontSize=10))])
    t = Table(data, colWidths=[A4[0]-80])
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (0, 0), HexColor('#f0f0f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return t


def _invoice_items_table(poliza, show_payment=True):
    data = [
        [Paragraph("<b>Description</b>", ParagraphStyle('th', fontSize=9)),
         Paragraph("<b>Montant</b>", ParagraphStyle('th', fontSize=9, alignment=TA_RIGHT))],
        [Paragraph(f"Police: {poliza.police}", ParagraphStyle('td', fontSize=9)),
         Paragraph("", ParagraphStyle('td'))],
        [Paragraph(f"Attestation: {poliza.attestation}", ParagraphStyle('td', fontSize=9)),
         Paragraph("", ParagraphStyle('td'))],
        [Paragraph(f"Type: {poliza.letype}", ParagraphStyle('td', fontSize=9)),
         Paragraph("", ParagraphStyle('td'))],
        [Paragraph(f"Produit: {poliza.produit}", ParagraphStyle('td', fontSize=9)),
         Paragraph("", ParagraphStyle('td'))],
        [Paragraph(f"Matricule: {poliza.matricule}", ParagraphStyle('td', fontSize=9)),
         Paragraph("", ParagraphStyle('td'))],
        [Paragraph(f"Du: {poliza.du.strftime('%d/%m/%Y') if poliza.du else 'N/A'}  Au: {poliza.au.strftime('%d/%m/%Y') if poliza.au else 'N/A'}", ParagraphStyle('td', fontSize=9)),
         Paragraph("", ParagraphStyle('td'))],
    ]
    if show_payment:
        data.append([Paragraph("<b>Prime totale</b>", ParagraphStyle('tdb', fontSize=10)),
                     Paragraph(f"<b>{poliza.totale} MAD</b>", ParagraphStyle('tdb', fontSize=10, alignment=TA_RIGHT))])
        data.append([Paragraph("Efectivo (Espèce)", ParagraphStyle('td', fontSize=9)),
                     Paragraph(f"{poliza.espece} MAD", ParagraphStyle('td', fontSize=9, alignment=TA_RIGHT))])
        data.append([Paragraph("Cheque", ParagraphStyle('td', fontSize=9)),
                     Paragraph(f"{poliza.cheque} MAD", ParagraphStyle('td', fontSize=9, alignment=TA_RIGHT))])
        data.append([Paragraph("Virement (Transferencia)", ParagraphStyle('td', fontSize=9)),
                     Paragraph(f"{poliza.virement} MAD", ParagraphStyle('td', fontSize=9, alignment=TA_RIGHT))])
        if poliza.reste > 0:
            data.append([Paragraph("<b>Reste à payer</b>", ParagraphStyle('tdb', fontSize=10, textColor=HexColor('#dc3545'))),
                         Paragraph(f"<b>{poliza.reste} MAD</b>", ParagraphStyle('tdb', fontSize=10, alignment=TA_RIGHT, textColor=HexColor('#dc3545')))])
        else:
            data.append([Paragraph("<b>Reste</b>", ParagraphStyle('tdb', fontSize=10)),
                         Paragraph(f"<b>0,00 MAD</b>", ParagraphStyle('tdb', fontSize=10, alignment=TA_RIGHT))])

    col_widths = [A4[0]-80-60, 60]
    t = Table(data, colWidths=col_widths)
    style_cmds = [
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t


def _terms_section():
    data = [
        [Paragraph("<b>Conditions de paiement:</b>", ParagraphStyle('term', fontSize=8)),
         Paragraph("Paiement à réception. Merci de votre confiance.", ParagraphStyle('term', fontSize=8))],
    ]
    t = Table(data, colWidths=[A4[0]-80])
    t.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t


def _footer_section():
    return Paragraph("<i>Document généré par Proyecto SIS - Merci de votre confiance</i>",
                     ParagraphStyle('foot', fontSize=7, alignment=TA_CENTER, textColor=HexColor('#999999')))


# ---------- INVOICE VIEWS ----------

def invoice_by_receipt(request, pk):
    poliza = get_object_or_404(Poliza, recu=pk)
    if not REPORTLAB_AVAILABLE:
        return HttpResponse("Reportlab no está instalado.", status=500)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    elements = []
    elements.append(_header_table("FACTURE", f"N° {poliza.recu}"))
    elements.append(Spacer(1, 15))
    elements.append(_client_info_table(poliza))
    elements.append(Spacer(1, 15))
    elements.append(_invoice_items_table(poliza, show_payment=True))
    elements.append(Spacer(1, 15))
    elements.append(_terms_section())
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", color=HexColor('#cccccc')))
    elements.append(_footer_section())
    doc.build(elements)
    return _build_pdf_response(buf, f'factura_{poliza.recu}.pdf')


def invoice_by_client(request, client_id):
    cliente = get_object_or_404(Cliente, code_client=client_id)
    polizas = Poliza.objects.filter(code_client=cliente.code_client).order_by('-recu')
    if not polizas.exists():
        return render(request, 'facturacion/sin_polizas.html', {'modal': 'factures'})
    if not REPORTLAB_AVAILABLE:
        return HttpResponse("Reportlab no está instalado.", status=500)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    elements = []
    elements.append(_header_table("RELEVÉ DE FACTURES", f"Client: {cliente.nom_client}"))
    elements.append(Spacer(1, 15))
    cl_data = [
        [Paragraph(f"<b>CLIENT:</b> {cliente.nom_client}", ParagraphStyle('cl', fontSize=10))],
        [Paragraph(f"Code: {cliente.code_client}", ParagraphStyle('cl', fontSize=10))],
    ]
    if cliente.telephone_client:
        cl_data.append([Paragraph(f"Tel: {cliente.telephone_client}", ParagraphStyle('cl', fontSize=10))])
    if cliente.email_client:
        cl_data.append([Paragraph(f"Email: {cliente.email_client}", ParagraphStyle('cl', fontSize=10))])
    cl_t = Table(cl_data, colWidths=[A4[0]-80])
    cl_t.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')), ('LEFTPADDING', (0, 0), (-1, -1), 8), ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
    elements.append(cl_t)
    elements.append(Spacer(1, 15))

    totales = polizas.aggregate(
        tot=Sum('totale'), esp=Sum('espece'), che=Sum('cheque'),
        vir=Sum('virement'), res=Sum('reste')
    )
    data = [
        [Paragraph("<b>Recibo</b>", ParagraphStyle('th', fontSize=8)),
         Paragraph("<b>Police</b>", ParagraphStyle('th', fontSize=8)),
         Paragraph("<b>Asegurado</b>", ParagraphStyle('th', fontSize=8)),
         Paragraph("<b>Total</b>", ParagraphStyle('th', fontSize=8, alignment=TA_RIGHT)),
         Paragraph("<b>Payé</b>", ParagraphStyle('th', fontSize=8, alignment=TA_RIGHT)),
         Paragraph("<b>Reste</b>", ParagraphStyle('th', fontSize=8, alignment=TA_RIGHT))],
    ]
    for p in polizas:
        paye = p.totale - p.reste
        data.append([
            Paragraph(str(p.recu), ParagraphStyle('td', fontSize=8)),
            Paragraph(p.police, ParagraphStyle('td', fontSize=8)),
            Paragraph(p.assure, ParagraphStyle('td', fontSize=8)),
            Paragraph(f"{p.totale} MAD", ParagraphStyle('td', fontSize=8, alignment=TA_RIGHT)),
            Paragraph(f"{paye} MAD", ParagraphStyle('td', fontSize=8, alignment=TA_RIGHT)),
            Paragraph(f"{p.reste} MAD", ParagraphStyle('td', fontSize=8, alignment=TA_RIGHT)),
        ])
    data.append([
        Paragraph("<b>Total</b>", ParagraphStyle('tdb', fontSize=8)),
        Paragraph("", ParagraphStyle('tdb', fontSize=8)),
        Paragraph("", ParagraphStyle('tdb', fontSize=8)),
        Paragraph(f"<b>{totales['tot'] or 0} MAD</b>", ParagraphStyle('tdb', fontSize=8, alignment=TA_RIGHT)),
        Paragraph(f"<b>{(totales['tot'] or 0) - (totales['res'] or 0)} MAD</b>", ParagraphStyle('tdb', fontSize=8, alignment=TA_RIGHT)),
        Paragraph(f"<b>{totales['res'] or 0} MAD</b>", ParagraphStyle('tdb', fontSize=8, alignment=TA_RIGHT)),
    ])
    col_widths = [45, 80, 100, 65, 65, 65]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#f0f0f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", color=HexColor('#cccccc')))
    elements.append(_footer_section())
    doc.build(elements)
    return _build_pdf_response(buf, f'facturas_cliente_{client_id}.pdf')


def invoice_by_receipt_excel(request, pk):
    poliza = get_object_or_404(Poliza, recu=pk)
    if not OPENPYXL_AVAILABLE:
        return HttpResponse("openpyxl no está instalado.", status=500)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Factura {poliza.recu}"

    header_font = Font(name='Calibri', bold=True, size=14, color='FFFFFF')
    header_fill = PatternFill(start_color='0D6EFD', end_color='0D6EFD', fill_type='solid')
    label_font = Font(name='Calibri', bold=True, size=10)
    normal_font = Font(name='Calibri', size=10)
    money_font = Font(name='Calibri', size=10)
    total_font = Font(name='Calibri', bold=True, size=11)
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    center = Alignment(horizontal='center', vertical='center')
    right_align = Alignment(horizontal='right', vertical='center')

    ws.merge_cells('A1:D1')
    ws['A1'] = COMPANY_NAME
    ws['A1'].font = header_font
    ws['A1'].fill = header_fill
    ws['A1'].alignment = center

    ws.merge_cells('A2:D2')
    ws['A2'] = COMPANY_ADDRESS
    ws['A2'].font = Font(name='Calibri', size=9, italic=True)
    ws['A2'].alignment = center

    ws.merge_cells('A3:D3')
    ws['A3'] = f"FACTURE N° {poliza.recu}"
    ws['A3'].font = Font(name='Calibri', bold=True, size=12)
    ws['A3'].alignment = center

    row = 5
    ws.cell(row=row, column=1, value='Client:').font = label_font
    ws.cell(row=row, column=2, value=f"{poliza.assure} {poliza.prenom}").font = normal_font
    ws.merge_cells(f'B{row}:D{row}')
    row += 1
    ws.cell(row=row, column=1, value='Code client:').font = label_font
    ws.cell(row=row, column=2, value=poliza.code_client).font = normal_font
    row += 1
    ws.cell(row=row, column=1, value='Téléphone:').font = label_font
    ws.cell(row=row, column=2, value=poliza.telefono).font = normal_font
    row += 1
    ws.cell(row=row, column=1, value='Email:').font = label_font
    ws.cell(row=row, column=2, value=poliza.email).font = normal_font

    row += 2
    headers = ['Description', 'Détails', '', 'Montant']
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col_idx, value=h)
        cell.font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
        cell.fill = PatternFill(start_color='0D6EFD', end_color='0D6EFD', fill_type='solid')
        cell.border = thin_border
        if col_idx == 4:
            cell.alignment = right_align
        else:
            cell.alignment = Alignment(horizontal='left', vertical='center')

    items = [
        ('Police', poliza.police),
        ('Attestation', poliza.attestation),
        ('Type', poliza.letype),
        ('Produit', poliza.produit),
        ('Matricule', poliza.matricule),
        ('Période', f"{poliza.du.strftime('%d/%m/%Y') if poliza.du else ''} - {poliza.au.strftime('%d/%m/%Y') if poliza.au else ''}"),
    ]
    row += 1
    for label, value in items:
        ws.cell(row=row, column=1, value=label).font = label_font
        ws.cell(row=row, column=1).border = thin_border
        ws.merge_cells(f'B{row}:C{row}')
        ws.cell(row=row, column=2, value=value).font = normal_font
        ws.cell(row=row, column=2).border = thin_border
        ws.cell(row=row, column=3).border = thin_border
        ws.cell(row=row, column=4).border = thin_border
        row += 1

    row += 1
    payment_items = [
        ('Prime totale', float(poliza.totale)),
        ('Efectivo (Espèce)', float(poliza.espece)),
        ('Cheque', float(poliza.cheque)),
        ('Virement (Transferencia)', float(poliza.virement)),
        ('Reste à payer', float(poliza.reste)),
    ]
    for label, amount in payment_items:
        ws.cell(row=row, column=1, value='').border = thin_border
        ws.merge_cells(f'B{row}:C{row}')
        ws.cell(row=row, column=2, value=label).font = total_font if label in ('Prime totale', 'Reste à payer') else normal_font
        ws.cell(row=row, column=2).border = thin_border
        ws.cell(row=row, column=3).border = thin_border
        cell = ws.cell(row=row, column=4, value=amount)
        cell.font = total_font if label in ('Prime totale', 'Reste à payer') else money_font
        cell.number_format = '#,##0.00'
        cell.alignment = right_align
        cell.border = thin_border
        if label == 'Reste à payer':
            cell.font = Font(name='Calibri', bold=True, size=11, color='DC3545')
        row += 1

    row += 2
    ws.merge_cells(f'A{row}:D{row}')
    ws.cell(row=row, column=1, value='Conditions de paiement: Paiement à réception.').font = Font(name='Calibri', size=8, italic=True)

    ws.column_dimensions['A'].width = 22
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 15

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="factura_{poliza.recu}.xlsx"'
    wb.save(response)
    return response


# ---------- STATEMENT VIEWS ----------

def statement_by_receipt(request, pk):
    poliza = get_object_or_404(Poliza, recu=pk)
    if not REPORTLAB_AVAILABLE:
        return HttpResponse("Reportlab no está instalado.", status=500)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    elements = []
    elements.append(_header_table("RELEVÉ", f"N° {poliza.recu}"))
    elements.append(Spacer(1, 15))
    elements.append(_client_info_table(poliza))
    elements.append(Spacer(1, 15))

    data = [
        [Paragraph("<b>Référence</b>", ParagraphStyle('th', fontSize=9)),
         Paragraph("<b>Détail</b>", ParagraphStyle('th', fontSize=9)),
         Paragraph("<b>Montant</b>", ParagraphStyle('th', fontSize=9, alignment=TA_RIGHT))],
        [Paragraph(f"Recibo N°", ParagraphStyle('td', fontSize=9)),
         Paragraph(str(poliza.recu), ParagraphStyle('td', fontSize=9)),
         Paragraph("", ParagraphStyle('td'))],
        [Paragraph("Police", ParagraphStyle('td', fontSize=9)),
         Paragraph(poliza.police, ParagraphStyle('td', fontSize=9)),
         Paragraph("", ParagraphStyle('td'))],
        [Paragraph("Attestation", ParagraphStyle('td', fontSize=9)),
         Paragraph(poliza.attestation, ParagraphStyle('td', fontSize=9)),
         Paragraph("", ParagraphStyle('td'))],
        [Paragraph("Produit", ParagraphStyle('td', fontSize=9)),
         Paragraph(poliza.produit, ParagraphStyle('td', fontSize=9)),
         Paragraph("", ParagraphStyle('td'))],
        [Paragraph("Période", ParagraphStyle('td', fontSize=9)),
         Paragraph(f"{poliza.du.strftime('%d/%m/%Y') if poliza.du else ''} au {poliza.au.strftime('%d/%m/%Y') if poliza.au else ''}", ParagraphStyle('td', fontSize=9)),
         Paragraph("", ParagraphStyle('td'))],
        [Paragraph("<b>Prime totale</b>", ParagraphStyle('tdb', fontSize=10)),
         Paragraph("", ParagraphStyle('tdb')),
         Paragraph(f"<b>{poliza.totale} MAD</b>", ParagraphStyle('tdb', fontSize=10, alignment=TA_RIGHT))],
    ]

    paye = poliza.totale - poliza.reste
    data.append([Paragraph("Montant payé", ParagraphStyle('td', fontSize=9)),
                 Paragraph("", ParagraphStyle('td')),
                 Paragraph(f"{paye} MAD", ParagraphStyle('td', fontSize=9, alignment=TA_RIGHT))])
    data.append([Paragraph("<b>Solde actuel</b>", ParagraphStyle('tdb', fontSize=10)),
                 Paragraph("", ParagraphStyle('tdb')),
                 Paragraph(f"<b>{poliza.reste} MAD</b>", ParagraphStyle('tdb', fontSize=10, alignment=TA_RIGHT))])

    col_widths = [100, A4[0]-80-100-60, 60]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#fff3cd')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", color=HexColor('#cccccc')))
    elements.append(_footer_section())
    doc.build(elements)
    return _build_pdf_response(buf, f'releve_{poliza.recu}.pdf')


def statement_by_client(request, client_id):
    cliente = get_object_or_404(Cliente, code_client=client_id)
    polizas = Poliza.objects.filter(code_client=cliente.code_client).order_by('-recu')
    if not polizas.exists():
        return render(request, 'facturacion/sin_polizas.html', {'modal': 'releves'})
    if not REPORTLAB_AVAILABLE:
        return HttpResponse("Reportlab no está instalado.", status=500)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    elements = []
    elements.append(_header_table("RELEVÉ DE COMPTE", f"Client: {cliente.nom_client}"))
    elements.append(Spacer(1, 15))
    cl_data = [
        [Paragraph(f"<b>CLIENT:</b> {cliente.nom_client}", ParagraphStyle('cl', fontSize=10))],
        [Paragraph(f"Code: {cliente.code_client}", ParagraphStyle('cl', fontSize=10))],
    ]
    if cliente.telephone_client:
        cl_data.append([Paragraph(f"Tel: {cliente.telephone_client}", ParagraphStyle('cl', fontSize=10))])
    cl_t = Table(cl_data, colWidths=[A4[0]-80])
    cl_t.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')), ('LEFTPADDING', (0, 0), (-1, -1), 8), ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
    elements.append(cl_t)
    elements.append(Spacer(1, 15))

    totales = polizas.aggregate(
        tot=Sum('totale'), esp=Sum('espece'), che=Sum('cheque'),
        vir=Sum('virement'), res=Sum('reste')
    )
    data = [
        [Paragraph("<b>Recibo</b>", ParagraphStyle('th', fontSize=8)),
         Paragraph("<b>Police</b>", ParagraphStyle('th', fontSize=8)),
         Paragraph("<b>Total</b>", ParagraphStyle('th', fontSize=8, alignment=TA_RIGHT)),
         Paragraph("<b>Payé</b>", ParagraphStyle('th', fontSize=8, alignment=TA_RIGHT)),
         Paragraph("<b>Solde</b>", ParagraphStyle('th', fontSize=8, alignment=TA_RIGHT))],
    ]
    for p in polizas:
        paye = p.totale - p.reste
        data.append([
            Paragraph(str(p.recu), ParagraphStyle('td', fontSize=8)),
            Paragraph(p.police, ParagraphStyle('td', fontSize=8)),
            Paragraph(f"{p.totale} MAD", ParagraphStyle('td', fontSize=8, alignment=TA_RIGHT)),
            Paragraph(f"{paye} MAD", ParagraphStyle('td', fontSize=8, alignment=TA_RIGHT)),
            Paragraph(f"{p.reste} MAD", ParagraphStyle('td', fontSize=8, alignment=TA_RIGHT)),
        ])
    total_paye = (totales['tot'] or 0) - (totales['res'] or 0)
    data.append([
        Paragraph("<b>Total</b>", ParagraphStyle('tdb', fontSize=8)),
        Paragraph("", ParagraphStyle('tdb')),
        Paragraph(f"<b>{totales['tot'] or 0} MAD</b>", ParagraphStyle('tdb', fontSize=8, alignment=TA_RIGHT)),
        Paragraph(f"<b>{total_paye} MAD</b>", ParagraphStyle('tdb', fontSize=8, alignment=TA_RIGHT)),
        Paragraph(f"<b>{totales['res'] or 0} MAD</b>", ParagraphStyle('tdb', fontSize=8, alignment=TA_RIGHT)),
    ])
    col_widths = [45, 100, 75, 75, 75]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#fff3cd')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", color=HexColor('#cccccc')))
    elements.append(_footer_section())
    doc.build(elements)
    return _build_pdf_response(buf, f'releve_cliente_{client_id}.pdf')


def statement_by_receipt_excel(request, pk):
    poliza = get_object_or_404(Poliza, recu=pk)
    if not OPENPYXL_AVAILABLE:
        return HttpResponse("openpyxl no está instalado.", status=500)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Relevé {poliza.recu}"

    header_font = Font(name='Calibri', bold=True, size=14, color='FFFFFF')
    header_fill = PatternFill(start_color='0D6EFD', end_color='0D6EFD', fill_type='solid')
    label_font = Font(name='Calibri', bold=True, size=10)
    normal_font = Font(name='Calibri', size=10)
    total_font = Font(name='Calibri', bold=True, size=11)
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    center = Alignment(horizontal='center', vertical='center')
    right_align = Alignment(horizontal='right', vertical='center')

    ws.merge_cells('A1:D1')
    ws['A1'] = COMPANY_NAME
    ws['A1'].font = header_font
    ws['A1'].fill = header_fill
    ws['A1'].alignment = center

    ws.merge_cells('A2:D2')
    ws['A2'] = COMPANY_ADDRESS
    ws['A2'].font = Font(name='Calibri', size=9, italic=True)
    ws['A2'].alignment = center

    ws.merge_cells('A3:D3')
    ws['A3'] = f"RELEVÉ N° {poliza.recu}"
    ws['A3'].font = Font(name='Calibri', bold=True, size=12)
    ws['A3'].alignment = center

    row = 5
    ws.cell(row=row, column=1, value='Client:').font = label_font
    ws.cell(row=row, column=2, value=f"{poliza.assure} {poliza.prenom}").font = normal_font
    ws.merge_cells(f'B{row}:D{row}')
    row += 1
    ws.cell(row=row, column=1, value='Police:').font = label_font
    ws.cell(row=row, column=2, value=poliza.police).font = normal_font
    ws.merge_cells(f'B{row}:D{row}')
    row += 1
    ws.cell(row=row, column=1, value='Attestation:').font = label_font
    ws.cell(row=row, column=2, value=poliza.attestation).font = normal_font
    ws.merge_cells(f'B{row}:D{row}')
    row += 1
    ws.cell(row=row, column=1, value='Produit:').font = label_font
    ws.cell(row=row, column=2, value=poliza.produit).font = normal_font
    ws.merge_cells(f'B{row}:D{row}')
    row += 1
    ws.cell(row=row, column=1, value='Période:').font = label_font
    ws.cell(row=row, column=2, value=f"{poliza.du.strftime('%d/%m/%Y') if poliza.du else ''} - {poliza.au.strftime('%d/%m/%Y') if poliza.au else ''}").font = normal_font
    ws.merge_cells(f'B{row}:D{row}')

    row += 2
    headers = ['Référence', 'Détail', '', 'Montant']
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col_idx, value=h)
        cell.font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
        cell.fill = PatternFill(start_color='0D6EFD', end_color='0D6EFD', fill_type='solid')
        cell.border = thin_border
        cell.alignment = right_align if col_idx == 4 else Alignment(horizontal='left', vertical='center')

    row += 1
    ws.merge_cells(f'A{row}:C{row}')
    ws.cell(row=row, column=1, value='Prime totale').font = normal_font
    ws.cell(row=row, column=1).border = thin_border
    ws.cell(row=row, column=2).border = thin_border
    ws.cell(row=row, column=3).border = thin_border
    cell = ws.cell(row=row, column=4, value=float(poliza.totale))
    cell.font = total_font
    cell.number_format = '#,##0.00'
    cell.alignment = right_align
    cell.border = thin_border
    row += 1

    paye = poliza.totale - poliza.reste
    ws.merge_cells(f'A{row}:C{row}')
    ws.cell(row=row, column=1, value='Montant payé').font = normal_font
    ws.cell(row=row, column=1).border = thin_border
    ws.cell(row=row, column=2).border = thin_border
    ws.cell(row=row, column=3).border = thin_border
    cell = ws.cell(row=row, column=4, value=float(paye))
    cell.font = normal_font
    cell.number_format = '#,##0.00'
    cell.alignment = right_align
    cell.border = thin_border
    row += 1

    ws.merge_cells(f'A{row}:C{row}')
    ws.cell(row=row, column=1, value='Solde actuel').font = Font(name='Calibri', bold=True, size=11, color='DC3545')
    ws.cell(row=row, column=1).border = thin_border
    ws.cell(row=row, column=2).border = thin_border
    ws.cell(row=row, column=3).border = thin_border
    cell = ws.cell(row=row, column=4, value=float(poliza.reste))
    cell.font = Font(name='Calibri', bold=True, size=11, color='DC3545')
    cell.number_format = '#,##0.00'
    cell.alignment = right_align
    cell.border = thin_border

    ws.column_dimensions['A'].width = 22
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 15

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="releve_{poliza.recu}.xlsx"'
    wb.save(response)
    return response


# ---------- BALANCE PENDIENTE ----------

def balance_pendiente_list(request):
    polizas = Poliza.objects.filter(reste__gt=0).order_by('-recu')
    total_general = polizas.aggregate(
        tot=Sum('totale'), res=Sum('reste')
    )

    if 'export_excel' in request.GET:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Balance Pendiente"
        headers = ['Recibo', 'Asegurado', 'Póliza', 'Total', 'Pagado', 'Reste', 'Teléfono']
        header_fill = PatternFill(start_color='0D6EFD', end_color='0D6EFD', fill_type='solid')
        header_font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
        for ci, h in enumerate(headers, 1):
            cell = ws.cell(row=1, column=ci, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.border = thin_border
        for ri, p in enumerate(polizas, 2):
            ws.cell(row=ri, column=1, value=p.recu).border = thin_border
            ws.cell(row=ri, column=2, value=str(p.assure)).border = thin_border
            ws.cell(row=ri, column=3, value=p.police).border = thin_border
            cell_t = ws.cell(row=ri, column=4, value=float(p.totale))
            cell_t.number_format = '#,##0.00'
            cell_t.border = thin_border
            pagado = float(p.totale - p.reste)
            cell_p = ws.cell(row=ri, column=5, value=pagado)
            cell_p.number_format = '#,##0.00'
            cell_p.border = thin_border
            cell_r = ws.cell(row=ri, column=6, value=float(p.reste))
            cell_r.number_format = '#,##0.00'
            cell_r.border = thin_border
            ws.cell(row=ri, column=7, value=p.telefono).border = thin_border
        ws.column_dimensions['A'].width = 10
        ws.column_dimensions['B'].width = 30
        ws.column_dimensions['C'].width = 18
        ws.column_dimensions['D'].width = 12
        ws.column_dimensions['E'].width = 12
        ws.column_dimensions['F'].width = 12
        ws.column_dimensions['G'].width = 18
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="balance_pendiente.xlsx"'
        wb.save(response)
        return response

    pagado_total = (total_general['tot'] or 0) - (total_general['res'] or 0)
    for p in polizas:
        p.pagado = p.totale - p.reste

    return render(request, 'facturacion/balance_pendiente.html', {
        'polizas': polizas,
        'total_general': total_general,
        'pagado_total': pagado_total,
    })


# ---------- CONSULTA VENCIMIENTO ----------

def consulta_vencimiento(request):
    resultados = None
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')

    if fecha_desde and fecha_hasta:
        resultados = Poliza.objects.filter(au__gte=fecha_desde, au__lte=fecha_hasta).order_by('au')

    if 'export_excel' in request.GET and resultados is not None:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Vencimientos"
        headers = ['Recibo', 'Asegurado', 'Póliza', 'Desde', 'Hasta', 'Teléfono', 'Email']
        header_fill = PatternFill(start_color='0D6EFD', end_color='0D6EFD', fill_type='solid')
        header_font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
        for ci, h in enumerate(headers, 1):
            cell = ws.cell(row=1, column=ci, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.border = thin_border
        for ri, p in enumerate(resultados, 2):
            ws.cell(row=ri, column=1, value=p.recu).border = thin_border
            ws.cell(row=ri, column=2, value=str(p.assure)).border = thin_border
            ws.cell(row=ri, column=3, value=p.police).border = thin_border
            ws.cell(row=ri, column=4, value=p.du.strftime('%d/%m/%Y') if p.du else '').border = thin_border
            ws.cell(row=ri, column=5, value=p.au.strftime('%d/%m/%Y') if p.au else '').border = thin_border
            ws.cell(row=ri, column=6, value=p.telefono).border = thin_border
            ws.cell(row=ri, column=7, value=p.email).border = thin_border
        ws.column_dimensions['A'].width = 10
        ws.column_dimensions['B'].width = 30
        ws.column_dimensions['C'].width = 18
        ws.column_dimensions['D'].width = 14
        ws.column_dimensions['E'].width = 14
        ws.column_dimensions['F'].width = 18
        ws.column_dimensions['G'].width = 30
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="consulta_vencimiento.xlsx"'
        wb.save(response)
        return response

    return render(request, 'facturacion/consulta_vencimiento.html', {
        'resultados': resultados,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    })


def invoice_list_by_client(request, client_id):
    polizas = Poliza.objects.filter(code_client=client_id).order_by('-recu')
    cliente = Cliente.objects.filter(code_client=client_id).first()
    cliente_nom = cliente.nom_client if cliente else str(client_id)

    if 'export_excel' in request.GET:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f'Facturas {client_id}'
        headers = ['Recibo', 'Fecha', 'Tipo', 'Póliza', 'Matrícula', 'Désignation',
                   'Prime Nette', 'Taxes', 'TP', 'Accessoires', 'Total TTC', 'Resto']
        header_fill = PatternFill(start_color='0D6EFD', end_color='0D6EFD', fill_type='solid')
        header_font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
        for col, h in enumerate(headers, 1):
            c = ws.cell(row=1, column=col, value=h)
            c.font = header_font
            c.fill = header_fill
            c.alignment = Alignment(horizontal='center')
        for row, p in enumerate(polizas, 2):
            ws.cell(row=row, column=1, value=p.recu)
            ws.cell(row=row, column=2, value=p.fecha_hoy.strftime('%d/%m/%Y') if p.fecha_hoy else '')
            ws.cell(row=row, column=3, value=p.letype)
            ws.cell(row=row, column=4, value=p.police)
            ws.cell(row=row, column=5, value=p.matricule)
            ws.cell(row=row, column=6, value=p.designation)
            ws.cell(row=row, column=7, value=float(p.prime_net))
            ws.cell(row=row, column=8, value=float(p.taxes))
            ws.cell(row=row, column=9, value=float(p.tp))
            ws.cell(row=row, column=10, value=float(p.accesoires))
            ws.cell(row=row, column=11, value=float(p.totale))
            ws.cell(row=row, column=12, value=float(p.reste))
        for col_letter in ['A','B','C','D','E','F','G','H','I','J','K','L']:
            ws.column_dimensions[col_letter].width = 15
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="facturas_{client_id}.xlsx"'
        wb.save(response)
        return response

    return render(request, 'facturacion/invoice_list_client.html', {
        'polizas': polizas,
        'cliente_nom': cliente_nom,
        'cliente_code': client_id,
    })


def statement_list_by_client(request, client_id):
    polizas = Poliza.objects.filter(code_client=client_id).order_by('-recu')
    cliente = Cliente.objects.filter(code_client=client_id).first()
    cliente_nom = cliente.nom_client if cliente else str(client_id)

    if 'export_excel' in request.GET:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f'Relevés {client_id}'
        headers = ['Recibo', 'Fecha', 'Tipo', 'Póliza', 'Matrícula', 'Désignation',
                   'Prime Nette', 'Taxes', 'TP', 'Accessoires', 'Total TTC', 'Resto']
        header_fill = PatternFill(start_color='198754', end_color='198754', fill_type='solid')
        header_font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
        for col, h in enumerate(headers, 1):
            c = ws.cell(row=1, column=col, value=h)
            c.font = header_font
            c.fill = header_fill
            c.alignment = Alignment(horizontal='center')
        for row, p in enumerate(polizas, 2):
            ws.cell(row=row, column=1, value=p.recu)
            ws.cell(row=row, column=2, value=p.fecha_hoy.strftime('%d/%m/%Y') if p.fecha_hoy else '')
            ws.cell(row=row, column=3, value=p.letype)
            ws.cell(row=row, column=4, value=p.police)
            ws.cell(row=row, column=5, value=p.matricule)
            ws.cell(row=row, column=6, value=p.designation)
            ws.cell(row=row, column=7, value=float(p.prime_net))
            ws.cell(row=row, column=8, value=float(p.taxes))
            ws.cell(row=row, column=9, value=float(p.tp))
            ws.cell(row=row, column=10, value=float(p.accesoires))
            ws.cell(row=row, column=11, value=float(p.totale))
            ws.cell(row=row, column=12, value=float(p.reste))
        for col_letter in ['A','B','C','D','E','F','G','H','I','J','K','L']:
            ws.column_dimensions[col_letter].width = 15
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="releves_{client_id}.xlsx"'
        wb.save(response)
        return response

    return render(request, 'facturacion/statement_list_client.html', {
        'polizas': polizas,
        'cliente_nom': cliente_nom,
        'cliente_code': client_id,
    })
