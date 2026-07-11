from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Experto


class ExpertoListView(ListView):
    model = Experto
    template_name = 'expertos/lista.html'
    context_object_name = 'expertos'


class ExpertoCreateView(CreateView):
    model = Experto
    template_name = 'expertos/form.html'
    fields = ['nom_expert']
    success_url = reverse_lazy('experto_list')


class ExpertoUpdateView(UpdateView):
    model = Experto
    template_name = 'expertos/form.html'
    fields = ['nom_expert']
    success_url = reverse_lazy('experto_list')


class ExpertoDeleteView(DeleteView):
    model = Experto
    template_name = 'expertos/confirm_delete.html'
    success_url = reverse_lazy('experto_list')
