import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import EmailMessage
from decouple import config


class Command(BaseCommand):
    help = 'Crea copia de seguridad de la base de datos y opcionalmente la envía por email'

    def add_arguments(self, parser):
        parser.add_argument('--no-email', action='store_true', help='No enviar email')
        parser.add_argument('--email-only', action='store_true', help='Solo enviar el último backup por email')

    def handle(self, *args, **options):
        backup_dir = Path('C:/copieSec')
        backup_dir.mkdir(parents=True, exist_ok=True)

        fecha = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        db_path = Path(settings.BASE_DIR) / 'db.sqlite3'

        if options['email_only']:
            files = sorted(backup_dir.glob('db-backup-*.sql'), reverse=True)
            if not files:
                self.stdout.write(self.style.ERROR('No hay backups previos'))
                return
            backup_file = files[0]
            self._send_email(backup_file)
            return

        sql_path = backup_dir / f'db-backup-{fecha}.sql'

        try:
            result = subprocess.run(
                ['sqlite3', str(db_path), '.dump'],
                capture_output=True, text=True, check=True
            )
            sql_path.write_text(result.stdout, encoding='utf-8')
            self.stdout.write(self.style.SUCCESS(f'Backup SQL creado: {sql_path}'))
        except (subprocess.CalledProcessError, FileNotFoundError):
            backup_file = backup_dir / f'db-backup-{fecha}.sqlite3'
            shutil.copy2(db_path, backup_file)
            sql_path = backup_file
            self.stdout.write(self.style.SUCCESS(f'Backup binario creado: {sql_path}'))

        log_path = backup_dir / 'log.txt'
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f'Backup creado: {fecha} - {sql_path.name}\n')

        if not options['no_email']:
            self._send_email(sql_path)

    def _send_email(self, filepath):
        emails = config('BACKUP_EMAILS', default='')
        if not emails:
            self.stdout.write(self.style.WARNING('No hay emails configurados para backup'))
            return

        to_list = [e.strip() for e in emails.split(',') if e.strip()]
        subject = f'Copia de seguridad BD - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        body = f'Adjunto copia de seguridad de la base de datos.\nFecha: {datetime.now().strftime("%Y-%m-%d %H:%M")}'

        msg = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, to_list)
        msg.attach(filepath.name, filepath.read_bytes(), 'application/sql')
        try:
            msg.send()
            self.stdout.write(self.style.SUCCESS('Email enviado correctamente'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al enviar email: {e}'))
