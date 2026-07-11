from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'model_name', 'record_id', 'action', 'user']
    list_filter = ['action', 'model_name']
    search_fields = ['model_name', 'record_id']
    readonly_fields = list_display + ['before', 'after', 'ip_address']
