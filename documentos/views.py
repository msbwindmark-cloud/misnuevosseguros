from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import TipoDocumento, DocumentoUsuario
from .forms import TipoDocumentoForm
from polizas.models import Poliza


class TipoDocumentoListView(ListView):
    model = TipoDocumento
    template_name = 'documentos/tipos_lista.html'
    context_object_name = 'tipos'


class TipoDocumentoCreateView(CreateView):
    model = TipoDocumento
    form_class = TipoDocumentoForm
    template_name = 'documentos/tipos_form.html'
    success_url = reverse_lazy('tipo_documento_list')


class TipoDocumentoUpdateView(UpdateView):
    model = TipoDocumento
    form_class = TipoDocumentoForm
    template_name = 'documentos/tipos_form.html'
    success_url = reverse_lazy('tipo_documento_list')


class TipoDocumentoDeleteView(DeleteView):
    model = TipoDocumento
    template_name = 'documentos/tipos_confirm_delete.html'
    success_url = reverse_lazy('tipo_documento_list')

    def form_valid(self, form):
        messages.success(self.request, f'Tipo de documento "{self.object}" eliminado correctamente.')
        return super().form_valid(form)


@staff_member_required
def add_document_to_poliza(request, recu=None):
    poliza = None
    documentos = []

    if recu:
        poliza = get_object_or_404(Poliza, pk=recu)
        documentos = DocumentoUsuario.objects.filter(id_usuario=recu).order_by('-creado_el')

    if request.method == 'POST':
        recu_post = request.POST.get('recu')
        poliza = get_object_or_404(Poliza, pk=recu_post)
        tipos_doc = request.POST.getlist('tipo_doc_modal[]')
        count = 0
        for idx, id_tipo in enumerate(tipos_doc):
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
                    tipo_documento_id=int(id_tipo) if id_tipo and id_tipo.isdigit() else None,
                    archivo=f,
                )
                count += 1

        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return JsonResponse({'ok': True, 'count': count, 'recu': poliza.recu})

        messages.success(request, f'{count} documento(s) añadido(s) a la póliza nº {poliza.recu}')
        return redirect('add_document_to_poliza', recu=poliza.recu)

    tipos = TipoDocumento.objects.all()
    polizas = Poliza.objects.all().order_by('-recu')
    return render(request, 'documentos/add_docs.html', {
        'poliza': poliza,
        'documentos': documentos,
        'tipos': tipos,
        'polizas': polizas,
    })


@staff_member_required
def consulter_documents_des_clients(request):
    doc_recus = DocumentoUsuario.objects.values_list('id_usuario', flat=True).distinct()
    polizas_con_docs = Poliza.objects.filter(recu__in=list(doc_recus)).order_by('-fecha_hoy')

    documentos_por_poliza = {}
    for p in polizas_con_docs:
        docs = DocumentoUsuario.objects.filter(id_usuario=p.recu).order_by('-creado_el')
        documentos_por_poliza[p] = docs

    return render(request, 'documentos/consulter_documents.html', {
        'documentos_por_poliza': documentos_por_poliza,
    })
