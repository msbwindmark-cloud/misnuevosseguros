from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from .models import Cliente, ClienteEliminado
from .forms import ClienteForm


class ClienteListView(ListView):
    model = Cliente
    template_name = 'clientes/lista.html'
    context_object_name = 'clientes'
    paginate_by = 50


class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/form.html'
    success_url = reverse_lazy('cliente_list')


@staff_member_required
def batch_client_entry(request):
    if request.method == 'POST':
        nombres = request.POST.getlist('nombre[]')
        apellidos = request.POST.getlist('apellidos[]')
        emails = request.POST.getlist('email[]')
        telefonos = request.POST.getlist('telefono[]')
        count = 0
        for i in range(len(nombres)):
            nom = nombres[i].strip()
            if not nom:
                continue
            Cliente.objects.create(
                code_client=str(int(__import__('time').time()))[-8:],
                nom_client=f"{nom} {apellidos[i]}".strip() if i < len(apellidos) else nom,
                telephone_client=telefonos[i] if i < len(telefonos) else '',
                email_client=emails[i] if i < len(emails) else '',
            )
            count += 1
        messages.success(request, f'{count} clientes añadidos correctamente.')
        return redirect('cliente_list')
    return render(request, 'clientes/batch_add.html')


@staff_member_required
def import_clientes_excel(request):
    if request.method == 'POST' and request.FILES.get('archivo'):
        import openpyxl
        wb = openpyxl.load_workbook(request.FILES['archivo'])
        ws = wb.active
        imported = 0
        for row in ws.iter_rows(min_row=2, values_only=True):
            code, nombre, telefono, email = (row + (None,)*4)[:4]
            if nombre:
                Cliente.objects.update_or_create(
                    code_client=code or '',
                    defaults={
                        'nom_client': str(nombre)[:200],
                        'telephone_client': str(telefono)[:50] if telefono else '',
                        'email_client': str(email)[:254] if email else '',
                    }
                )
                imported += 1
        messages.success(request, f'{imported} clientes importados correctamente.')
        return redirect('cliente_list')
    return render(request, 'clientes/import.html')


class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/form.html'
    success_url = reverse_lazy('cliente_list')


class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = 'clientes/confirm_delete.html'
    success_url = reverse_lazy('cliente_list')
    success_message = 'Cliente eliminado correctamente'

    def delete(self, request, *args, **kwargs):
        cliente = self.get_object()
        ClienteEliminado.objects.create(
            code_client=cliente.code_client,
            nom_client=cliente.nom_client,
            telephone_client=cliente.telephone_client,
            email_client=cliente.email_client,
            address_client=cliente.address_client,
        )
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@staff_member_required
def cliente_bulk_delete(request):
    if request.method == 'POST':
        pks = request.POST.getlist('pk')
        count = 0
        for cliente in Cliente.objects.filter(pk__in=pks):
            ClienteEliminado.objects.create(
                code_client=cliente.code_client,
                nom_client=cliente.nom_client,
                telephone_client=cliente.telephone_client,
                email_client=cliente.email_client,
                address_client=cliente.address_client,
            )
            cliente.delete()
            count += 1
        if count == 1:
            messages.success(request, 'Cliente eliminado correctamente')
        elif count > 1:
            messages.success(request, f'{count} clientes eliminados correctamente')
        else:
            messages.error(request, 'No se eliminó ningún cliente')
    return redirect('cliente_list')
