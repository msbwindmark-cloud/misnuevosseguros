import json, os, qrcode
from io import BytesIO
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from .models import Poliza, PolizaGarantia, PolizaGarantiaOption, PolizaGarantiaFranchise
from garantias.models import Garantia, GarantiaOption, GarantiaFranchise
from clientes.models import Cliente
from documentos.models import TipoDocumento, DocumentoUsuario
from attestations.models import TypeAttestation


class PolizaListView(ListView):
    model = Poliza
    template_name = 'polizas/lista.html'
    context_object_name = 'polizas'
    paginate_by = None

    def get_queryset(self):
        qs = super().get_queryset()
        from documentos.models import DocumentoUsuario
        if self.request.GET.get('con_docs') == '1':
            doc_ids = set(DocumentoUsuario.objects.values_list('id_usuario', flat=True).distinct())
            qs = qs.filter(recu__in=doc_ids)
        q = self.request.GET.get('q')
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(police__icontains=q) |
                Q(assure__icontains=q) |
                Q(matricule__icontains=q) |
                Q(recu__icontains=q)
            )
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        if fecha_desde:
            qs = qs.filter(fecha_hoy__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha_hoy__lte=fecha_hasta)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        recus = list(Poliza.objects.values_list('recu', flat=True))
        from documentos.models import DocumentoUsuario
        doc_ids = set(DocumentoUsuario.objects.filter(id_usuario__in=recus).values_list('id_usuario', flat=True).distinct())
        ctx['polizas_con_docs'] = doc_ids
        docs_count = DocumentoUsuario.objects.filter(id_usuario__in=recus).values('id_usuario').annotate(total=Count('id')).values_list('id_usuario', 'total')
        ctx['docs_count'] = {r: t for r, t in docs_count}
        ctx['filtrando_docs'] = self.request.GET.get('con_docs') == '1'
        ctx['q'] = self.request.GET.get('q', '')
        ctx['fecha_desde'] = self.request.GET.get('fecha_desde', '')
        ctx['fecha_hasta'] = self.request.GET.get('fecha_hasta', '')
        ctx['filtando_fechas'] = bool(self.request.GET.get('fecha_desde') or self.request.GET.get('fecha_hasta'))
        ctx['clientes'] = Cliente.objects.all().order_by('code_client')
        ctx['clientes_con_poliza'] = set(
            str(c) for c in Poliza.objects.exclude(code_client='')
            .values_list('code_client', flat=True).distinct()
        )
        return ctx


class PolizaDetailView(DetailView):
    model = Poliza
    template_name = 'polizas/detalle.html'
    context_object_name = 'poliza'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        poliza = self.object
        data = []
        for pg in poliza.garantias.select_related('garantia').all():
            item = {'id': pg.garantia_id, 'nom': pg.garantia.nom_garantie, 'valeur': str(pg.valeur) if pg.valeur else ''}
            opt = poliza.garantias_options.filter(garantia=pg.garantia).select_related('option').first()
            if opt:
                item['option'] = {'id': opt.option_id, 'nom': opt.option.nom_option, 'valeur': str(opt.valeur) if opt.valeur else ''}
            fr = poliza.garantias_franquicias.filter(garantia=pg.garantia).select_related('franchise').first()
            if fr:
                item['franchise'] = {'id': fr.franchise_id, 'nom': fr.franchise.nom_franchise, 'montant': str(fr.montant_franchise) if fr.montant_franchise else ''}
            data.append(item)
        ctx['garantias_data'] = data
        return ctx


GARANTIAS_CON_OPCIONES = {9, 10, 13, 14, 17, 19}
GARANTIAS_CON_MONTANT_DIRECTO = {7, 8}


def _build_val(poliza=None):
    """Build a dict of all form field values for the poliza template."""
    from datetime import date as dt_date
    v = {f: '' for f in [
        'recu', 'fecha_hoy', 'letype', 'attestation', 'police', 'marque', 'matricule',
        'produit', 'designation', 'assure', 'prenom', 'code_client', 'telefono', 'email',
        'address_client', 'du', 'au', 'prime_net', 'taxes', 'tp', 'accesoires',
        'totale', 'espece', 'cheque', 'virement', 'reste', 'date_versement',
    ]}
    if poliza:
        for f in v:
            val = getattr(poliza, f, None)
            if val is None:
                v[f] = ''
            elif isinstance(val, (dt_date,)):
                v[f] = val.strftime('%Y-%m-%d')
            elif isinstance(val, Decimal):
                v[f] = str(val)
            else:
                v[f] = str(val)
    else:
        v['recu'] = str((Poliza.objects.order_by('-recu').first().recu + 1) if Poliza.objects.exists() else 1)
        v['fecha_hoy'] = datetime.now().strftime('%Y-%m-%d')
    return v


class PolizaCreateView(View):
    template_name = 'polizas/form.html'

    def get(self, request):
        garantias = Garantia.objects.all()
        tipos_doc = TipoDocumento.objects.all()
        tipos_attestation = TypeAttestation.objects.all()
        garantias_opciones = GARANTIAS_CON_OPCIONES
        garantias_montant = GARANTIAS_CON_MONTANT_DIRECTO
        saved_recu = request.GET.get('saved')
        poliza_saved = None
        if saved_recu:
            try:
                poliza_saved = Poliza.objects.get(pk=int(saved_recu))
            except (Poliza.DoesNotExist, ValueError):
                pass
        return render(request, self.template_name, {
            'val': _build_val(),
            'garantias': garantias,
            'tipos_doc': tipos_doc,
            'tipos_attestation': tipos_attestation,
            'garantias_opciones': garantias_opciones,
            'garantias_montant': garantias_montant,
            'garantias_data_json': '[]',
            'poliza_saved': poliza_saved,
            'doc_obligatorios': request.GET.get('doc_obligatorios', ''),
        })

    def post(self, request):
        data = request.POST
        files = request.FILES

        required = ['letype', 'assure', 'police', 'attestation', 'du', 'au', 'totale', 'produit', 'matricule', 'marque']
        errors = {}
        for field in required:
            if not data.get(field, '').strip():
                errors[field] = 'Ce champ est obligatoire'
        if not data.get('doc_obligatorios'):
            tiene_doc = any(len(files.getlist(k)) > 0 for k in files if k.startswith('archivos_modal_'))
            tiene_reutilizados = len(data.getlist('docs_reutilizados')) > 0
            if not tiene_doc and not tiene_reutilizados:
                errors['documentos'] = 'Vous devez joindre au moins un document pour enregistrer la póliza.'

        try:
            garantias_validacion = json.loads(data.get('garantias_data', '[]'))
        except json.JSONDecodeError:
            garantias_validacion = []
        attest_val = data.get('attestation', '').strip()
        # Les garanties sont obligatoires uniquement si une attestation réelle est
        # renseignée (chargée via "Consulter Attestation"). Un simple point "." ou un
        # champ vide indique qu'elles ne le sont pas.
        if attest_val and attest_val != '.':
            if not garantias_validacion:
                errors['garantias'] = 'Vous devez sélectionner au moins une garantie.'

        if errors:
            val = _build_val()
            for f in val:
                val[f] = data.get(f, val[f])
            garantias = Garantia.objects.all()
            tipos_doc = TipoDocumento.objects.all()
            tipos_attestation = TypeAttestation.objects.all()
            for key, msg in errors.items():
                messages.error(request, f'{key}: {msg}')
            return render(request, self.template_name, {
                'val': val,
                'garantias': garantias,
                'tipos_doc': tipos_doc,
                'tipos_attestation': tipos_attestation,
                'garantias_opciones': GARANTIAS_CON_OPCIONES,
                'garantias_montant': GARANTIAS_CON_MONTANT_DIRECTO,
                'garantias_data_json': data.get('garantias_data', '[]'),
                'errors': errors,
                'doc_obligatorios': data.get('doc_obligatorios', ''),
            })

        def dv(key):
            val = data.get(key, '0')
            if not val or not str(val).strip():
                return Decimal('0')
            return Decimal(str(val).replace(',', '.'))

        reste = dv('totale') - dv('espece') - dv('cheque') - dv('virement')

        mode_paiment_parts = []
        if data.get('modo_espece'): mode_paiment_parts.append('espece')
        if data.get('modo_cheque'): mode_paiment_parts.append('cheque')
        if data.get('modo_virement'): mode_paiment_parts.append('virement')
        mode_paiment = ','.join(mode_paiment_parts) if mode_paiment_parts else 'nulo'

        poliza = Poliza.objects.create(
            fecha_hoy=data.get('fecha_hoy') or None,
            letype=data.get('letype', ''),
            attestation=data.get('attestation', ''),
            police=data.get('police', ''),
            marque=data.get('marque', ''),
            matricule=data.get('matricule', ''),
            produit=data.get('produit', ''),
            designation=data.get('designation', ''),
            assure=data.get('assure', ''),
            prenom=data.get('prenom', ''),
            du=data.get('du') or None,
            au=data.get('au') or None,
            prime_net=dv('prime_net'),
            taxes=dv('taxes'),
            tp=dv('tp'),
            accesoires=dv('accesoires'),
            totale=dv('totale'),
            espece=dv('espece'),
            cheque=dv('cheque'),
            virement=dv('virement'),
            reste=reste,
            date_versement=data.get('date_versement') or None,
            code_client=data.get('code_client', ''),
            telefono=data.get('telefono', ''),
            email=data.get('email', ''),
            address_client=data.get('address_client', ''),
            mode_paiment=mode_paiment,
        )

        if poliza.attestation:
            from attestations.models import Attestation as Att
            Att.objects.filter(numero_attestation=poliza.attestation).update(seleccionado=False)

        garantias_json = data.get('garantias_data', '[]')
        try:
            garantias_seleccionadas = json.loads(garantias_json)
        except json.JSONDecodeError:
            garantias_seleccionadas = []

        for g in garantias_seleccionadas:
            gid = int(g.get('id_garantie'))
            garantia = get_object_or_404(Garantia, pk=gid)
            id_option = g.get('id_option')
            id_franchise = g.get('id_franchise')
            montant_str = (g.get('montant') or '0').replace(',', '.')
            montant = Decimal(montant_str) if montant_str.strip() else None

            if id_franchise and id_option:
                option = get_object_or_404(GarantiaOption, pk=int(id_option))
                franchise = get_object_or_404(GarantiaFranchise, pk=int(id_franchise))
                PolizaGarantiaFranchise.objects.create(
                    poliza=poliza, garantia=garantia,
                    option=option, franchise=franchise,
                    montant_franchise=montant
                )
            elif id_option:
                option = get_object_or_404(GarantiaOption, pk=int(id_option))
                PolizaGarantiaOption.objects.create(
                    poliza=poliza, garantia=garantia,
                    option=option, valeur=montant
                )
            else:
                PolizaGarantia.objects.create(
                    poliza=poliza, garantia=garantia, valeur=montant
                )

        qr_data_str = (f"{poliza.assure}_{poliza.prenom}_{poliza.letype}_{poliza.attestation}_"
                       f"{poliza.police}_{poliza.matricule}_{poliza.produit}_"
                       f"{poliza.du}_{poliza.au}_{poliza.totale}_"
                       f"{poliza.espece}_{poliza.cheque}_{poliza.virement}_{poliza.reste}_"
                       f"{poliza.telefono}_{poliza.email}")
        qr_dir = settings.MEDIA_ROOT / 'qrcodes'
        qr_dir.mkdir(parents=True, exist_ok=True)
        qr_filename = f'qr_{poliza.recu}_{datetime.now().strftime("%Y%m%d%H%M%S")}.png'
        qr_path = qr_dir / qr_filename
        img = qrcode.make(qr_data_str)
        img.save(str(qr_path))

        tipos_doc = data.getlist('tipo_doc_modal[]')
        for idx, id_tipo in enumerate(tipos_doc):
            if not id_tipo:
                continue
            file_key = f'archivos_modal_{idx}'
            archivos = files.getlist(file_key)
            for f in archivos:
                doc = DocumentoUsuario(
                    id_usuario=poliza.recu,
                    nombre_documento_usuario=f.name,
                    tipo_documento_usuario=f.name.split('.')[-1].lower() if '.' in f.name else '',
                    tamanio_documento_usuario=f.size,
                    tipo_documento_id=int(id_tipo) if id_tipo.isdigit() else None,
                    archivo=f,
                )
                doc.save()

        for doc_id in data.getlist('docs_reutilizados'):
            try:
                orig = DocumentoUsuario.objects.get(pk=int(doc_id))
            except (DocumentoUsuario.DoesNotExist, ValueError):
                continue
            DocumentoUsuario.objects.create(
                id_usuario=poliza.recu,
                nombre_documento_usuario=orig.nombre_documento_usuario,
                tipo_documento_usuario=orig.tipo_documento_usuario,
                tamanio_documento_usuario=orig.tamanio_documento_usuario,
                tipo_documento=orig.tipo_documento,
                archivo=orig.archivo.name if orig.archivo else '',
                id_documento_usuario_origen=orig.id,
            )

        messages.success(request, f'Póliza nº {poliza.recu} creada correctamente.')
        return redirect(f"{reverse('poliza_create')}?saved={poliza.recu}")


def get_garantia_options(request, pk):
    options = GarantiaOption.objects.filter(garantia_id=pk).values('id', 'nom_option', 'requires_montant')
    return JsonResponse(list(options), safe=False)


def get_option_franchises(request, pk):
    franchises = GarantiaFranchise.objects.filter(option_id=pk).values('id', 'nom_franchise')
    return JsonResponse(list(franchises), safe=False)


def get_clientes_json(request):
    q = request.GET.get('q', '')
    clientes = Cliente.objects.all()
    if q:
        clientes = clientes.filter(nom_client__icontains=q) | clientes.filter(code_client__icontains=q)
    clientes = clientes.order_by('code_client')[:100]
    data = [{'id': c.pk, 'code': str(c.code_client), 'nom': str(c.nom_client),
             'tel': str(c.telephone_client or ''), 'email': str(c.email_client or '')} for c in clientes]
    return JsonResponse(data, safe=False)


@csrf_exempt
def crear_cliente_ajax(request):
    if request.method == 'POST':
        code = request.POST.get('code_client', '')
        nom = request.POST.get('nom_client', '')
        tel = request.POST.get('telephone_client', '')
        email = request.POST.get('email_client', '')
        if not nom:
            return JsonResponse({'ok': False, 'error': 'Nombre requerido'})
        cliente = Cliente.objects.create(
            code_client=code or int(datetime.now().timestamp()),
            nom_client=nom,
            telephone_client=tel or '',
            email_client=email or '',
        )
        return JsonResponse({
            'ok': True,
            'cliente': {
                'id': cliente.pk,
                'code': str(cliente.code_client),
                'nom': str(cliente.nom_client),
                'tel': str(cliente.telephone_client or ''),
                'email': str(cliente.email_client or ''),
            }
        })
    return JsonResponse({'ok': False, 'error': 'Método no permitido'})


def get_attestations_json(request):
    from attestations.models import Attestation
    q = request.GET.get('q', '')
    atts = Attestation.objects.select_related('id_type_attestation').all()
    if q:
        atts = atts.filter(numero_attestation__icontains=q) | atts.filter(id_type_attestation__type_attestation__icontains=q)
    data = [{'id': a.pk, 'type': str(a.id_type_attestation.type_attestation),
             'numero': str(a.numero_attestation), 'active': a.seleccionado} for a in atts.order_by('-pk')[:100]]
    return JsonResponse(data, safe=False)


def get_next_attestation(request):
    from attestations.models import Attestation
    type_id = request.GET.get('type_id', '')
    if not type_id or not type_id.isdigit():
        return JsonResponse({'ok': False, 'error': 'type_id requerido'})
    att = Attestation.objects.filter(
        id_type_attestation_id=int(type_id),
        seleccionado=True
    ).order_by('-id').first()
    if att:
        return JsonResponse({'ok': True, 'numero': str(att.numero_attestation), 'id': att.pk})
    return JsonResponse({'ok': False, 'error': 'No hay attestations disponibles para este tipo'})


@csrf_exempt
def crear_attestation_ajax(request):
    if request.method == 'POST':
        from attestations.models import Attestation, TypeAttestation
        type_id = request.POST.get('type_attestation', '')
        numero = request.POST.get('numero_attestation', '')
        if not type_id or not numero:
            return JsonResponse({'ok': False, 'error': 'Tipo y número requeridos'})
        att = Attestation.objects.create(
            id_type_attestation_id=type_id,
            numero_attestation=numero,
        )
        return JsonResponse({
            'ok': True,
            'attestation': {
                'id': att.pk,
                'type': str(att.id_type_attestation.type_attestation),
                'numero': str(att.numero_attestation),
            }
        })
    return JsonResponse({'ok': False, 'error': 'Método no permitido'})


def get_polizas_json(request):
    q = request.GET.get('q', '')
    polizas = Poliza.objects.all()
    if q:
        polizas = polizas.filter(police__icontains=q) | polizas.filter(assure__icontains=q) | polizas.filter(matricule__icontains=q)
    data = [{
        'id': p.pk, 'recu': str(p.recu), 'fecha': str(p.fecha_hoy or ''),
        'police': str(p.police or ''), 'marque': str(p.marque or ''),
        'matricule': str(p.matricule or ''), 'produit': str(p.produit or ''),
        'designation': str(p.designation or ''), 'assure': str(p.assure or ''),
        'code_client': str(p.code_client or ''),
        'tel': str(p.telefono or ''), 'email': str(p.email or ''),
        'adresse': str(p.address_client or ''),
        'attestation': str(p.attestation or ''),
        'fecha_hoy': str(p.fecha_hoy or ''),
        'du': str(p.du or ''), 'au': str(p.au or ''),
    } for p in polizas.order_by('-pk')[:100]]
    return JsonResponse(data, safe=False)


@login_required
def poliza_datatables_data(request):
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 50))
    search_value = request.GET.get('search[value]', '')
    order_col = int(request.GET.get('order[0][column]', 1))
    order_dir = request.GET.get('order[0][dir]', 'desc')

    col_map = {1: 'recu', 2: 'fecha_hoy', 3: 'letype', 4: 'police',
               5: 'matricule', 6: 'assure', 7: 'totale', 8: 'reste'}
    order_field = col_map.get(order_col, 'recu')
    if order_dir == 'desc':
        order_field = '-' + order_field

    qs = Poliza.objects.all()
    if search_value:
        from django.db.models import Q
        qs = qs.filter(
            Q(police__icontains=search_value) |
            Q(assure__icontains=search_value) |
            Q(matricule__icontains=search_value) |
            Q(recu__icontains=search_value)
        )

    records_total = Poliza.objects.count()
    records_filtered = qs.count()
    polizas = qs.order_by(order_field)[start:start + length]

    data = []
    for p in polizas:
        data.append({
            'recu': p.recu,
            'fecha_hoy': p.fecha_hoy.strftime('%d/%m/%Y') if p.fecha_hoy else '',
            'letype': p.letype or '',
            'police': p.police or '',
            'matricule': p.matricule or '',
            'assure': str(p.assure or ''),
            'totale': str(p.totale or ''),
            'reste': str(p.reste or ''),
        })
    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data,
    })


def poliza_docs_by_police(request):
    police = request.GET.get('police', '').strip()
    if not police:
        return JsonResponse([], safe=False)
    recus = list(Poliza.objects.filter(police=police).values_list('recu', flat=True))
    docs = (DocumentoUsuario.objects
            .filter(id_usuario__in=recus)
            .select_related('tipo_documento')
            .order_by('-id'))
    data = [{
        'id': d.id,
        'nombre': d.nombre_documento_usuario or '',
        'tipo': d.tipo_documento.tipo_documento if d.tipo_documento else 'Sin tipo',
        'url': d.archivo.url if d.archivo else '',
    } for d in docs]
    return JsonResponse(data, safe=False)


class PolizaUpdateView(View):
    template_name = 'polizas/form.html'

    def get(self, request, pk):
        poliza = get_object_or_404(Poliza, pk=pk)
        garantias = Garantia.objects.all()
        tipos_doc = TipoDocumento.objects.all()
        tipos_attestation = TypeAttestation.objects.all()
        garantias_data = []
        for pg in poliza.garantias.select_related('garantia').all():
            item = {'id': pg.garantia_id, 'valeur': str(pg.valeur) if pg.valeur else ''}
            opt = poliza.garantias_options.filter(garantia=pg.garantia).first()
            if opt:
                item['option'] = {'id': opt.option_id, 'valeur': str(opt.valeur) if opt.valeur else ''}
            fr = poliza.garantias_franquicias.filter(garantia=pg.garantia).first()
            if fr:
                item['franchise'] = {'id': fr.franchise_id, 'montant': str(fr.montant_franchise) if fr.montant_franchise else ''}
            garantias_data.append(item)
        return render(request, self.template_name, {
            'poliza': poliza,
            'val': _build_val(poliza),
            'garantias': garantias,
            'tipos_doc': tipos_doc,
            'tipos_attestation': tipos_attestation,
            'garantias_opciones': GARANTIAS_CON_OPCIONES,
            'garantias_montant': GARANTIAS_CON_MONTANT_DIRECTO,
            'editing': True,
            'garantias_data_json': json.dumps(garantias_data),
        })

    def post(self, request, pk):
        poliza = get_object_or_404(Poliza, pk=pk)
        data = request.POST

        def dv(key):
            val = data.get(key, '0')
            if not val or not str(val).strip():
                return Decimal('0')
            return Decimal(str(val).replace(',', '.'))

        reste = dv('totale') - dv('espece') - dv('cheque') - dv('virement')
        mode_paiment_parts = []
        if data.get('modo_espece'): mode_paiment_parts.append('espece')
        if data.get('modo_cheque'): mode_paiment_parts.append('cheque')
        if data.get('modo_virement'): mode_paiment_parts.append('virement')
        mode_paiment = ','.join(mode_paiment_parts) if mode_paiment_parts else 'nulo'
        for field in ['fecha_hoy', 'letype', 'attestation', 'police', 'marque', 'matricule',
                       'produit', 'designation', 'assure', 'prenom', 'du', 'au', 'prime_net',
                       'taxes', 'tp', 'accesoires', 'totale', 'espece', 'cheque', 'virement',
                       'date_versement', 'code_client', 'telefono', 'email', 'address_client']:
            val = data.get(field)
            if val is not None:
                if field in ('totale', 'espece', 'cheque', 'virement', 'prime_net', 'taxes', 'tp', 'accesoires'):
                    val = dv(field)
                elif field in ('fecha_hoy', 'du', 'au', 'date_versement'):
                    val = val or None
                setattr(poliza, field, val)
        poliza.reste = reste
        poliza.mode_paiment = mode_paiment
        poliza.save()

        tipos_doc_up = data.getlist('tipo_doc_modal[]')
        for idx, id_tipo in enumerate(tipos_doc_up):
            if not id_tipo:
                continue
            file_key = f'archivos_modal_{idx}'
            archivos = request.FILES.getlist(file_key)
            for f in archivos:
                DocumentoUsuario.objects.create(
                    id_usuario=poliza.recu,
                    nombre_documento_usuario=f.name,
                    tipo_documento_usuario=f.name.split('.')[-1].lower() if '.' in f.name else '',
                    tamanio_documento_usuario=f.size,
                    tipo_documento_id=int(id_tipo) if id_tipo.isdigit() else None,
                    archivo=f,
                )
        for doc_id in data.getlist('docs_reutilizados'):
            try:
                orig = DocumentoUsuario.objects.get(pk=int(doc_id))
            except (DocumentoUsuario.DoesNotExist, ValueError):
                continue
            DocumentoUsuario.objects.create(
                id_usuario=poliza.recu,
                nombre_documento_usuario=orig.nombre_documento_usuario,
                tipo_documento_usuario=orig.tipo_documento_usuario,
                tamanio_documento_usuario=orig.tamanio_documento_usuario,
                tipo_documento=orig.tipo_documento,
                archivo=orig.archivo.name if orig.archivo else '',
                id_documento_usuario_origen=orig.id,
            )

        poliza.garantias.all().delete()
        poliza.garantias_options.all().delete()
        poliza.garantias_franquicias.all().delete()
        i = 0
        while f'garantia_{i}' in data:
            gid = data.get(f'garantia_{i}')
            if gid:
                g = get_object_or_404(Garantia, pk=int(gid))
                valeur = data.get(f'valeur_directe_{i}') or None
                if valeur is not None:
                    try:
                        valeur = Decimal(str(valeur).replace(',', '.'))
                    except:
                        valeur = None
                PolizaGarantia.objects.create(poliza=poliza, garantia=g, valeur=valeur)
                opt_id = data.get(f'option_{i}')
                if opt_id:
                    opt = get_object_or_404(GarantiaOption, pk=int(opt_id))
                    opt_val = data.get(f'option_valeur_{i}') or None
                    if opt_val is not None:
                        try:
                            opt_val = Decimal(str(opt_val).replace(',', '.'))
                        except:
                            opt_val = None
                    PolizaGarantiaOption.objects.create(poliza=poliza, garantia=g, option=opt, valeur=opt_val)
                    fr_id = data.get(f'franchise_{i}')
                    if fr_id:
                        fr = get_object_or_404(GarantiaFranchise, pk=int(fr_id))
                        fr_montant = data.get(f'montant_franchise_{i}') or None
                        if fr_montant is not None:
                            try:
                                fr_montant = Decimal(str(fr_montant).replace(',', '.'))
                            except:
                                fr_montant = None
                        PolizaGarantiaFranchise.objects.create(poliza=poliza, garantia=g, option=opt, franchise=fr, montant_franchise=fr_montant)
            i += 1
        attest_code = data.get('attestation', '').strip()
        if attest_code:
            from attestations.models import Attestation
            Attestation.objects.filter(numero_attestation=attest_code).update(seleccionado=False)
        messages.success(request, 'Póliza actualizada correctamente')
        return redirect('poliza_list')


def poliza_garantias_data(request, pk):
    poliza = get_object_or_404(Poliza, pk=pk)
    data = []
    for pg in poliza.garantias.select_related('garantia').all():
        item = {'id': pg.garantia_id, 'nom': pg.garantia.nom_garantie, 'valeur': str(pg.valeur) if pg.valeur else ''}
        opt = poliza.garantias_options.filter(garantia=pg.garantia).first()
        if opt:
            item['option'] = {'id': opt.option_id, 'nom': opt.option.nom_option, 'valeur': str(opt.valeur) if opt.valeur else ''}
        fr = poliza.garantias_franquicias.filter(garantia=pg.garantia).first()
        if fr:
            item['franchise'] = {'id': fr.franchise_id, 'nom': fr.franchise.nom_franchise, 'montant': str(fr.montant_franchise) if fr.montant_franchise else ''}
        data.append(item)
    return JsonResponse({'garantias': data})


def poliza_documents_data(request, pk):
    from documentos.models import DocumentoUsuario
    docs = DocumentoUsuario.objects.filter(id_usuario=pk).order_by('-creado_el')
    data = []
    for d in docs:
        data.append({
            'id': d.id,
            'nombre': d.nombre_documento_usuario,
            'tipo': d.tipo_documento.nombre if d.tipo_documento else (d.tipo_documento_usuario or '—'),
            'tamanio': d.tamanio_documento_usuario,
            'fecha': d.creado_el.strftime('%d/%m/%Y %H:%M') if d.creado_el else '',
            'archivo': d.archivo.url if d.archivo else '',
            'origen': d.id_documento_usuario_origen,
            'heredado': bool(d.id_documento_usuario_origen),
        })
    return JsonResponse({'documentos': data})


@staff_member_required
def poliza_documentos_agregar(request, pk):
    from documentos.models import DocumentoUsuario
    poliza = get_object_or_404(Poliza, pk=pk)
    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        count = 0
        tipos_doc = data.getlist('tipo_doc_modal[]')
        for idx, id_tipo in enumerate(tipos_doc):
            if not id_tipo:
                continue
            file_key = f'archivos_modal_{idx}'
            archivos = files.getlist(file_key)
            for f in archivos:
                DocumentoUsuario.objects.create(
                    id_usuario=poliza.recu,
                    nombre_documento_usuario=f.name,
                    tipo_documento_usuario=f.name.split('.')[-1].lower() if '.' in f.name else '',
                    tamanio_documento_usuario=f.size,
                    tipo_documento_id=int(id_tipo) if id_tipo.isdigit() else None,
                    archivo=f,
                )
                count += 1
        for doc_id in data.getlist('docs_reutilizados'):
            try:
                orig = DocumentoUsuario.objects.get(pk=int(doc_id))
            except (DocumentoUsuario.DoesNotExist, ValueError):
                continue
            DocumentoUsuario.objects.create(
                id_usuario=poliza.recu,
                nombre_documento_usuario=orig.nombre_documento_usuario,
                tipo_documento_usuario=orig.tipo_documento_usuario,
                tamanio_documento_usuario=orig.tamanio_documento_usuario,
                tipo_documento=orig.tipo_documento,
                archivo=orig.archivo.name if orig.archivo else '',
                id_documento_usuario_origen=orig.id,
            )
            count += 1
        messages.success(request, f'{count} documento(s) añadido(s) a la póliza nº {poliza.recu}')
        return redirect('poliza_list')
    return redirect('poliza_list')
