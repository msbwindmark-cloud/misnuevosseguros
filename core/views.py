from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from io import BytesIO
from polizas.models import Poliza, PolizaEliminada
from clientes.models import Cliente, ClienteEliminado
from siniestros.models import Sinistro
from pathlib import Path
from audit.number_text import montant_en_lettres


@staff_member_required
def export_polizas_pdf(request):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph('Lista de Pólizas', styles['Title']))
    elements.append(Spacer(1, 0.5*cm))
    data = [['Recibo', 'Fecha', 'Asegurado', 'Póliza', 'Matrícula', 'Total', 'Resto']]
    for p in Poliza.objects.all().order_by('-recu')[:100]:
        fecha = p.fecha_hoy.strftime('%d/%m/%Y') if p.fecha_hoy else ''
        data.append([str(p.recu), fecha, p.assure, p.police, p.matricule, str(p.totale), str(p.reste)])
    table = Table(data, colWidths=[2*cm, 2.5*cm, 4*cm, 3*cm, 3*cm, 2*cm, 2*cm])
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
    # Total row
    total_global = sum(float(p.totale) for p in Poliza.objects.all()[:100])
    data.append(['', '', '', '', 'TOTAL:', f'{total_global:.2f}', ''])
    table = Table(data, colWidths=[2*cm, 2.5*cm, 4*cm, 3*cm, 3*cm, 2*cm, 2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4e73df')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (4, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fc')]),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5*cm))
    normal_txt = ParagraphStyle('NormalCite', parent=styles['Normal'], fontSize=9, leading=12, fontName='Helvetica-Oblique')
    elements.append(Paragraph(
        f'<i>Arrêté le présent état récapitulatif à la somme totale de : {montant_en_lettres(total_global)}</i>',
        normal_txt
    ))
    doc.build(elements)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', headers={
        'Content-Disposition': 'attachment; filename="polizas.pdf"'
    })


@staff_member_required
def export_polizas_excel(request):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Pólizas'
    headers = ['Recibo', 'Fecha', 'Tipo', 'Atestación', 'Póliza', 'Marca', 'Matrícula',
               'Producto', 'Asegurado', 'Desde', 'Hasta', 'Total', 'Efectivo', 'Cheque',
               'Transferencia', 'Resto']
    header_fill = PatternFill(start_color='4e73df', end_color='4e73df', fill_type='solid')
    header_font = Font(color='ffffff', bold=True)
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
    polizas = Poliza.objects.all().order_by('-recu')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    if fecha_desde:
        polizas = polizas.filter(fecha_hoy__gte=fecha_desde)
    if fecha_hasta:
        polizas = polizas.filter(fecha_hoy__lte=fecha_hasta)
    for row, p in enumerate(polizas, 2):
        ws.cell(row=row, column=1, value=p.recu)
        ws.cell(row=row, column=2, value=p.fecha_hoy.strftime('%d/%m/%Y') if p.fecha_hoy else '')
        ws.cell(row=row, column=3, value=p.letype)
        ws.cell(row=row, column=4, value=p.attestation)
        ws.cell(row=row, column=5, value=p.police)
        ws.cell(row=row, column=6, value=p.marque)
        ws.cell(row=row, column=7, value=p.matricule)
        ws.cell(row=row, column=8, value=p.produit)
        ws.cell(row=row, column=9, value=p.assure)
        ws.cell(row=row, column=10, value=p.du.strftime('%d/%m/%Y') if p.du else '')
        ws.cell(row=row, column=11, value=p.au.strftime('%d/%m/%Y') if p.au else '')
        ws.cell(row=row, column=12, value=float(p.totale))
        ws.cell(row=row, column=13, value=float(p.espece))
        ws.cell(row=row, column=14, value=float(p.cheque))
        ws.cell(row=row, column=15, value=float(p.virement))
        ws.cell(row=row, column=16, value=float(p.reste))
    for col in range(1, len(headers)+1):
        ws.column_dimensions[chr(64+col)].width = 15
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="polizas.xlsx"'
    wb.save(response)
    return response


@staff_member_required
def export_clientes_excel(request):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Clientes'
    headers = ['Código', 'Nombre', 'Teléfono', 'Email', 'Creado']
    header_fill = PatternFill(start_color='1cc88a', end_color='1cc88a', fill_type='solid')
    header_font = Font(color='ffffff', bold=True)
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
    for row, c in enumerate(Cliente.objects.all().order_by('code_client'), 2):
        ws.cell(row=row, column=1, value=c.code_client)
        ws.cell(row=row, column=2, value=c.nom_client)
        ws.cell(row=row, column=3, value=c.telephone_client)
        ws.cell(row=row, column=4, value=c.email_client)
        ws.cell(row=row, column=5, value=c.creado_el.strftime('%d/%m/%Y') if c.creado_el else '')
    for col in range(1, len(headers)+1):
        ws.column_dimensions[chr(64+col)].width = 20
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="clientes.xlsx"'
    wb.save(response)
    return response


def _build_receipt_pdf(poliza, first_logo, first_footer, second_logo, second_footer, filename):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    page_w, page_h = A4

    logo_path = Path(settings.BASE_DIR / 'static' / 'images' / 'logo.png')
    firma_path = Path(settings.BASE_DIR / 'static' / 'images' / 'firma_atlanta.png')
    footer_path = Path(settings.BASE_DIR / 'static' / 'images' / 'footer.GIF')

    garantias_lines = []
    for g in poliza.garantias.select_related('garantia').all():
        line = f'- {g.garantia.nom_garantie}'
        opt = poliza.garantias_options.filter(garantia=g.garantia).first()
        if opt:
            line += f' - {opt.option.nom_option}' + (f' ({opt.valeur})' if opt.valeur else '')
        fr = poliza.garantias_franquicias.filter(garantia=g.garantia).first()
        if fr:
            line += f' - Franchise: {fr.franchise.nom_franchise}' + (f' ({fr.montant_franchise})' if fr.montant_franchise else '')
        if g.valeur:
            line += f' : {g.valeur}'
        garantias_lines.append(line)

    du_str = poliza.du.strftime('%d/%m/%Y') if poliza.du else ''
    au_str = poliza.au.strftime('%d/%m/%Y') if poliza.au else ''

    def draw_block(offset_y, with_logo, with_footer):
        def ty(fpdf_y):
            return page_h - (fpdf_y + offset_y) * mm

        if with_logo and logo_path.exists():
            c.drawImage(str(logo_path), 5*mm, ty(5+24), width=180*mm, height=24*mm, preserveAspectRatio=True, mask='auto')

        c.setFont('Helvetica-Bold', 9)
        c.drawString(120*mm, ty(45), 'Garanties :')
        c.setFont('Helvetica', 8)
        gy = 48
        for line in garantias_lines:
            c.drawString(120*mm, ty(gy), line[:80])
            gy += 5

        c.setFont('Helvetica', 10)
        c.drawString(15*mm, ty(30), f'Re\u00e7u N\u00b0 : {poliza.recu}')
        c.setLineWidth(0.5)
        c.rect(15*mm, ty(38), 4*mm, 4*mm)
        c.setFont('Helvetica', 9)
        c.drawString(21*mm, ty(38), f'Type Affaire : {poliza.letype}')
        c.drawString(100*mm, ty(38), f'Code Client : {poliza.code_client}')
        c.drawString(15*mm, ty(44), f'N\u00b0 Police : {poliza.police}')
        c.drawString(15*mm, ty(48), f'Attestation : {poliza.attestation}')
        c.drawString(15*mm, ty(52), f'Assur\u00e9 : {poliza.assure} {poliza.prenom}')
        c.drawString(15*mm, ty(56), f'P\u00e9riode : Du : {du_str}    Au : {au_str}')

        pay_items = [
            ('PRIME TOTALE', str(poliza.totale)),
            ('ESPECE', str(poliza.espece)),
            ('CHEQUE', str(poliza.cheque)),
            ('VIREMENT', str(poliza.virement)),
            ('RESTE A REGLER', str(poliza.reste)),
        ]
        table_top_y = 64
        row_h = 5
        col_w = 54
        c.setFont('Helvetica-Bold', 9)
        c.setStrokeColor(colors.black)
        for i, (label, val) in enumerate(pay_items):
            y = ty(table_top_y + i * row_h)
            c.rect(15*mm, y, col_w*mm, row_h*mm)
            c.rect((15+col_w)*mm, y, col_w*mm, row_h*mm)
            c.drawCentredString((15 + col_w/2)*mm, y + 1.2*mm, label)
            val_str = f'{val} MAD'
            c.drawCentredString((15 + col_w + col_w/2)*mm, y + 1.2*mm, val_str)

        c.setFont('Helvetica', 8)
        c.drawString(15*mm, ty(93), f'Arr\u00eat\u00e9 la pr\u00e9sente quittance \u00e0 la somme de : {montant_en_lettres(poliza.totale)}')

        c.setFont('Helvetica', 9)
        c.drawString(15*mm, ty(99), 'Signature Production')
        sig_y = 104
        if firma_path.exists():
            c.drawImage(str(firma_path), 15*mm, ty(sig_y)-15*mm, width=30*mm, height=15*mm, preserveAspectRatio=True, mask='auto')
        c.drawString(75*mm, ty(99), 'Signature Client')

        if with_footer and footer_path.exists():
            c.drawImage(str(footer_path), 3*mm, ty(120+27), width=200*mm, height=27*mm, preserveAspectRatio=True, mask='auto')

    draw_block(0, with_logo=first_logo, with_footer=first_footer)
    draw_block(145, with_logo=second_logo, with_footer=second_footer)

    c.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', headers={
        'Content-Disposition': f'attachment; filename="{filename}"'
    })


@staff_member_required
def generate_poliza_pdf(request, pk):
    try:
        poliza = Poliza.objects.get(pk=pk)
    except Poliza.DoesNotExist:
        return HttpResponse('P\u00f3liza no encontrada', status=404)
    return _build_receipt_pdf(poliza, True, True, True, True, f'recu_{poliza.recu}.pdf')


@staff_member_required
def generate_poliza_pdf_sans_entete(request, pk):
    try:
        poliza = Poliza.objects.get(pk=pk)
    except Poliza.DoesNotExist:
        return HttpResponse('P\u00f3liza no encontrada', status=404)
    return _build_receipt_pdf(poliza, False, True, True, False, f'recu_{poliza.recu}_sans_entete.pdf')


@staff_member_required
def generate_poliza_pdf_with_header(request, pk):
    return generate_poliza_pdf(request, pk)


@staff_member_required
def poliza_list_delete(request):
    from django.shortcuts import redirect
    from django.contrib import messages
    if request.method == 'POST':
        pk = request.POST.get('pk')
        if pk:
            try:
                p = Poliza.objects.get(pk=pk)
                import datetime
                PolizaEliminada.objects.create(
                    recu=p.recu, fecha_hoy=p.fecha_hoy, letype=p.letype,
                    attestation=p.attestation, police=p.police, matricule=p.matricule,
                    produit=p.produit, assure=p.assure, du=p.du, au=p.au,
                    totale=p.totale, espece=p.espece, cheque=p.cheque, virement=p.virement,
                    reste=p.reste, date_versement=p.date_versement, mode_paiment=p.mode_paiment,
                    cree_le=p.cree_le,
                )
                p.delete()
                messages.success(request, 'Póliza eliminada correctamente')
            except Poliza.DoesNotExist:
                messages.error(request, 'Póliza no encontrada')
        return redirect('poliza_list')
    return redirect('poliza_list')


@staff_member_required
def export_polizas_eliminadas_excel(request):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Eliminadas'
    headers = ['Recibo', 'Fecha', 'Tipo', 'Atestación', 'Póliza', 'Matrícula', 'Asegurado',
               'Total', 'Resto', 'Eliminado Por']
    header_fill = PatternFill(start_color='e74a3b', end_color='e74a3b', fill_type='solid')
    header_font = Font(color='ffffff', bold=True)
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
    for row, p in enumerate(PolizaEliminada.objects.all().order_by('-recu'), 2):
        ws.cell(row=row, column=1, value=p.recu)
        ws.cell(row=row, column=2, value=p.fecha_hoy.strftime('%d/%m/%Y') if p.fecha_hoy else '')
        ws.cell(row=row, column=3, value=p.letype)
        ws.cell(row=row, column=4, value=p.attestation)
        ws.cell(row=row, column=5, value=p.police)
        ws.cell(row=row, column=6, value=p.matricule)
        ws.cell(row=row, column=7, value=p.assure)
        ws.cell(row=row, column=8, value=float(p.totale))
        ws.cell(row=row, column=9, value=float(p.reste))
        ws.cell(row=row, column=10, value='')
    for col in range(1, len(headers)+1):
        ws.column_dimensions[chr(64+col)].width = 18
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="polizas_eliminadas.xlsx"'
    wb.save(response)
    return response


@staff_member_required
def export_expertos_pdf(request):
    from expertos.models import Experto
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph('Lista de Expertos', styles['Title']))
    elements.append(Spacer(1, 0.5*cm))
    data = [['Nombre', 'Teléfono', 'Email']]
    for e in Experto.objects.all():
        data.append([e.nombre, e.telefono or '', e.email or ''])
    table = Table(data, colWidths=[6*cm, 5*cm, 6*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4e73df')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', headers={
        'Content-Disposition': 'attachment; filename="expertos.pdf"'
    })


@staff_member_required
def check_expiring_ajax(request):
    from datetime import date, timedelta
    from django.http import JsonResponse
    target = date.today() + timedelta(days=3)
    polizas = Poliza.objects.filter(au=target)
    data = []
    for p in polizas:
        data.append({
            'assure': f'{p.assure} {p.prenom}',
            'police': p.police,
            'au': p.au.strftime('%d/%m/%Y') if p.au else '',
            'telefono': p.telefono,
            'email': p.email,
        })
    return JsonResponse({'count': len(data), 'polizas': data})


@staff_member_required
def backup_view(request):
    from datetime import datetime
    from pathlib import Path
    import subprocess
    import shutil
    from django.core.mail import EmailMessage
    from decouple import config

    backup_dir = Path('C:/copieSec')
    backup_dir.mkdir(parents=True, exist_ok=True)

    context = {}
    log_path = backup_dir / 'log.txt'
    if log_path.exists():
        context['log_lines'] = log_path.read_text(encoding='utf-8').splitlines()[-20:]

    if request.method == 'POST':
        action = request.POST.get('action', 'backup')
        fecha = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        db_path = Path(settings.BASE_DIR) / 'db.sqlite3'

        if action == 'backup':
            sql_path = backup_dir / f'db-backup-{fecha}.sql'
            try:
                result = subprocess.run(
                    ['sqlite3', str(db_path), '.dump'],
                    capture_output=True, text=True, check=True
                )
                sql_path.write_text(result.stdout, encoding='utf-8')
            except (subprocess.CalledProcessError, FileNotFoundError):
                sql_path = backup_dir / f'db-backup-{fecha}.sqlite3'
                shutil.copy2(db_path, sql_path)

            context['backup_file'] = sql_path.name
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f'Backup creado: {fecha} - {sql_path.name}\n')
            messages.success(request, f'Copia de seguridad creada: {sql_path.name}')

            # Auto-enviar por email como en el PHP original
            emails = config('BACKUP_EMAILS', default='')
            to_list = [e.strip() for e in emails.split(',') if e.strip()]
            if to_list:
                msg = EmailMessage(
                    f'Copia de seguridad BD - {fecha}',
                    f'Adjunto copia de seguridad.\nFecha: {fecha}',
                    settings.DEFAULT_FROM_EMAIL, to_list
                )
                msg.attach(sql_path.name, sql_path.read_bytes(), 'application/sql')
                try:
                    msg.send()
                    messages.success(request, 'Email enviado correctamente')
                except Exception as e:
                    messages.error(request, f'Error al enviar email: {e}')
            else:
                messages.warning(request, 'No hay emails configurados')

        return render(request, 'core/backup.html', context)

    return render(request, 'core/backup.html', context)


@staff_member_required
def export_clientes_eliminados_excel(request):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Clientes Eliminados'
    headers = ['Código', 'Nombre', 'Teléfono', 'Email', 'Eliminado el']
    header_fill = PatternFill(start_color='DC3545', end_color='DC3545', fill_type='solid')
    header_font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=col, value=h)
        c.font = header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal='center')
    for row, cl in enumerate(ClienteEliminado.objects.all().order_by('-eliminado_el'), 2):
        ws.cell(row=row, column=1, value=cl.code_client)
        ws.cell(row=row, column=2, value=cl.nom_client)
        ws.cell(row=row, column=3, value=cl.telephone_client)
        ws.cell(row=row, column=4, value=cl.email_client)
        ws.cell(row=row, column=5, value=cl.eliminado_el.strftime('%d/%m/%Y %H:%M') if cl.eliminado_el else '')
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 40
    ws.column_dimensions['C'].width = 18
    ws.column_dimensions['D'].width = 30
    ws.column_dimensions['E'].width = 20
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="clientes_eliminados.xlsx"'
    wb.save(response)
    return response


@staff_member_required
def export_cliente_pdf(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'],
                                  textColor=colors.HexColor('#4e73df'))
    elements.append(Paragraph('La fiche du Client', title_style))
    elements.append(Spacer(1, 0.5*cm))

    data = [
        ['Campo', 'Valor'],
        ['ID Nº', str(cliente.code_client)],
        ['Nom Client', cliente.nom_client],
        ['Email Client', cliente.email_client or '—'],
        ['Téléphone Client', cliente.telephone_client or '—'],
    ]
    table = Table(data, colWidths=[5*cm, 10*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4e73df')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f8f9fc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 1.5*cm))

    signature_style = ParagraphStyle('Signature', parent=styles['Normal'],
                                      fontSize=11, alignment=1)
    elements.append(Paragraph('Signature Production', signature_style))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph('Signature Client', signature_style))

    doc.build(elements)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', headers={
        'Content-Disposition': f'attachment; filename="cliente_{cliente.code_client}.pdf"'
    })


@staff_member_required
def escanear_qr(request):
    return render(request, 'core/escanear_qr.html')
