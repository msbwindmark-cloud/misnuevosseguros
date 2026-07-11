from django.urls import reverse_lazy
from django.views.generic import ListView, View, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Garantia, GarantiaOption, GarantiaFranchise
from .forms import GarantiaForm


class GarantiaListView(ListView):
    model = Garantia
    template_name = 'garantias/lista.html'
    context_object_name = 'garantias'


class GarantiaCreateView(View):
    template_name = 'garantias/form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': GarantiaForm()})

    def post(self, request):
        form = GarantiaForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})
        garantia = form.save()
        self._save_options(garantia, request.POST)
        messages.success(request, f'Garantía "{garantia.nom_garantie}" creada correctamente.')
        return redirect('garantia_list')

    def _save_options(self, garantia, post_data):
        noms = post_data.getlist('option_nom[]')
        requires = post_data.getlist('option_requires_montant[]')
        for i, nom in enumerate(noms):
            if not nom.strip():
                continue
            opt = GarantiaOption.objects.create(
                garantia=garantia,
                nom_option=nom.strip(),
                requires_montant=(requires[i] == 'on') if i < len(requires) else False,
            )
            franchises = post_data.getlist(f'franchise_nom_{i}[]')
            for fnom in franchises:
                if fnom.strip():
                    GarantiaFranchise.objects.create(
                        option=opt, nom_franchise=fnom.strip()
                    )


class GarantiaUpdateView(View):
    template_name = 'garantias/form.html'

    def get(self, request, pk):
        garantia = get_object_or_404(Garantia, pk=pk)
        form = GarantiaForm(instance=garantia)
        options = GarantiaOption.objects.filter(garantia=garantia).prefetch_related('franquicias')
        return render(request, self.template_name, {
            'form': form, 'garantia': garantia, 'options': options,
        })

    def post(self, request, pk):
        garantia = get_object_or_404(Garantia, pk=pk)
        form = GarantiaForm(request.POST, instance=garantia)
        if not form.is_valid():
            options = GarantiaOption.objects.filter(garantia=garantia).prefetch_related('franquicias')
            return render(request, self.template_name, {
                'form': form, 'garantia': garantia, 'options': options,
            })
        garantia = form.save()
        # Replace all options and franchises
        garantia.opciones.all().delete()
        self._save_options(garantia, request.POST)
        messages.success(request, f'Garantía "{garantia.nom_garantie}" actualizada correctamente.')
        return redirect('garantia_list')

    def _save_options(self, garantia, post_data):
        noms = post_data.getlist('option_nom[]')
        requires = post_data.getlist('option_requires_montant[]')
        for i, nom in enumerate(noms):
            if not nom.strip():
                continue
            opt = GarantiaOption.objects.create(
                garantia=garantia,
                nom_option=nom.strip(),
                requires_montant=(requires[i] == 'on') if i < len(requires) else False,
            )
            franchises = post_data.getlist(f'franchise_nom_{i}[]')
            for fnom in franchises:
                if fnom.strip():
                    GarantiaFranchise.objects.create(
                        option=opt, nom_franchise=fnom.strip()
                    )


class GarantiaDeleteView(DeleteView):
    model = Garantia
    template_name = 'garantias/confirm_delete.html'
    success_url = reverse_lazy('garantia_list')
