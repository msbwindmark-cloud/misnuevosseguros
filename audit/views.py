from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import AuditLog


@staff_member_required
def audit_list(request):
    model_name = request.GET.get('model', '')
    action = request.GET.get('action', '')
    logs = AuditLog.objects.select_related('user').all()
    if model_name:
        logs = logs.filter(model_name=model_name)
    if action:
        logs = logs.filter(action=action)
    models_list = (
        AuditLog.objects.values_list('model_name', flat=True)
        .distinct().order_by('model_name')
    )
    return render(request, 'audit/lista.html', {
        'logs': logs[:500],
        'models_list': models_list,
        'selected_model': model_name,
        'selected_action': action,
    })
