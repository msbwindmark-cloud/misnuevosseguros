from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from audit.models import AuditLog
from audit.middleware import _audit_thread, get_audit_user, get_audit_ip
from audit.utils import instance_to_dict

# Solo auditar modelos de nuestras apps
TRACKED_APPS = [
    'usuarios', 'clientes', 'polizas', 'siniestros',
    'garantias', 'banco', 'courrier', 'documentos',
    'expertos', 'attestations', 'facturacion',
]


def _should_track(sender):
    if sender == AuditLog:
        return False
    app_label = getattr(sender._meta, 'app_label', '')
    return app_label in TRACKED_APPS


@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    if not _should_track(sender):
        return
    stack = getattr(_audit_thread, 'before_stack', None)
    if stack is None:
        return
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            stack.append(instance_to_dict(original))
        except sender.DoesNotExist:
            stack.append(None)
    else:
        stack.append(None)


@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if not _should_track(sender):
        return
    stack = getattr(_audit_thread, 'before_stack', None)
    if not stack:
        return
    before = stack.pop() if stack else None
    after = instance_to_dict(instance)
    user = get_audit_user()
    ip = get_audit_ip()
    AuditLog.objects.create(
        model_name=sender.__name__,
        record_id=str(instance.pk),
        action='CREATE' if created else 'UPDATE',
        user=user,
        before=before,
        after=after,
        ip_address=ip,
    )


@receiver(pre_delete)
def audit_pre_delete(sender, instance, **kwargs):
    if not _should_track(sender):
        return
    before = instance_to_dict(instance)
    user = get_audit_user()
    ip = get_audit_ip()
    AuditLog.objects.create(
        model_name=sender.__name__,
        record_id=str(instance.pk),
        action='DELETE',
        user=user,
        before=before,
        after=None,
        ip_address=ip,
    )
