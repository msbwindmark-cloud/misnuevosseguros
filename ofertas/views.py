from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from .models import Oferta, TipoVehiculo, ModalidadSeguro, DuracionOferta, EstadoOferta
from .forms import OfertaForm


class OfertaListView(ListView):
    model = Oferta
    template_name = 'ofertas/lista.html'
    context_object_name = 'ofertas'


class OfertaCreateView(CreateView):
    model = Oferta
    form_class = OfertaForm
    template_name = 'ofertas/form.html'
    success_url = reverse_lazy('oferta_list')

    def form_valid(self, form):
        messages.success(self.request, 'Oferta creada correctamente.')
        return super().form_valid(form)


class OfertaUpdateView(UpdateView):
    model = Oferta
    form_class = OfertaForm
    template_name = 'ofertas/form.html'
    success_url = reverse_lazy('oferta_list')

    def form_valid(self, form):
        messages.success(self.request, 'Oferta actualizada correctamente.')
        return super().form_valid(form)


class OfertaDeleteView(DeleteView):
    model = Oferta
    template_name = 'ofertas/confirm_delete.html'
    success_url = reverse_lazy('oferta_list')

    def form_valid(self, form):
        messages.success(self.request, 'Oferta eliminada correctamente.')
        return super().form_valid(form)


def tipo_vehiculo_api(request):
    items = list(TipoVehiculo.objects.filter(activo=True).order_by('orden', 'nombre').values('id', 'nombre'))
    return JsonResponse({'results': items})


def modalidad_api(request):
    items = list(ModalidadSeguro.objects.filter(activo=True).order_by('orden', 'nombre').values('id', 'nombre', 'descripcion'))
    return JsonResponse({'results': items})


def duracion_api(request):
    items = list(DuracionOferta.objects.filter(activo=True).order_by('orden', 'meses').values('id', 'nombre', 'meses'))
    return JsonResponse({'results': items})


def estado_oferta_api(request):
    items = list(EstadoOferta.objects.filter(activo=True).order_by('orden', 'nombre').values('id', 'nombre', 'color'))
    return JsonResponse({'results': items})
