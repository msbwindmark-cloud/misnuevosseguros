from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from polizas.models import Poliza
from decouple import config


class Command(BaseCommand):
    help = 'Verifica pólizas que vencen en 3 días y envía notificaciones'

    def handle(self, *args, **options):
        target = date.today() + timedelta(days=3)
        polizas = Poliza.objects.filter(au=target)

        if not polizas.exists():
            self.stdout.write('No hay pólizas por vencer en 3 días')
            return

        to_email = config('NOTIFICATION_EMAIL', default='')
        if not to_email:
            self.stdout.write(self.style.WARNING('NOTIFICATION_EMAIL no configurado'))
            return

        lines = []
        for p in polizas:
            lines.append(
                f'Cliente: {p.assure} {p.prenom}\n'
                f'Póliza: {p.police}\n'
                f'Vencimiento: {p.au}\n'
                f'Teléfono: {p.telefono}\n'
                f'Email: {p.email}\n'
                f'---'
            )
            self.stdout.write(f'  - {p.assure} {p.prenom} - Póliza {p.police} - vence {p.au}')

        body = (
            f'Notificación de vencimiento de pólizas de seguro\n'
            f'Fecha: {date.today()}\n\n'
            f'Las siguientes pólizas vencen en 3 días ({target}):\n\n'
            + '\n'.join(lines)
        )

        try:
            send_mail(
                subject=f'Notificación vencimiento pólizas - {date.today()}',
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
            )
            self.stdout.write(self.style.SUCCESS(f'Notificación enviada a {to_email}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al enviar email: {e}'))
