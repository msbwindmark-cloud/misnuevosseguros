import pymysql
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from datetime import datetime


class Command(BaseCommand):
    help = 'Migra datos desde MySQL (proyectosis) a SQLite'

    def handle(self, *args, **options):
        self.stdout.write('Conectando a MySQL...')
        conn = pymysql.connect(
            host='localhost', user='root', password='', database='proyectosis',
            charset='utf8mb4'
        )
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 1. Migrar usuarios
        self.stdout.write('Migrando usuarios...')
        from usuarios.models import Usuario
        cursor.execute('SELECT * FROM users')
        for row in cursor.fetchall():
            Usuario.objects.update_or_create(
                id=row['id'],
                defaults={
                    'username': row.get('username', f'user_{row["id"]}'),
                    'email': row.get('email', ''),
                    'password': row.get('password', make_password('default123')),
                    'telefono': row.get('telephone', ''),
                    'is_staff': True,
                    'is_active': True,
                }
            )

        # 2. Migrar clientes
        self.stdout.write('Migrando clientes...')
        from clientes.models import Cliente
        cursor.execute('SELECT * FROM liste_des_clients')
        for row in cursor.fetchall():
            Cliente.objects.update_or_create(
                id=row['id'],
                defaults={
                    'code_client': row.get('code_client', ''),
                    'nom_client': row.get('nom_client', ''),
                    'telephone_client': row.get('telephone_client', ''),
                    'email_client': row.get('email_client', ''),
                    'creado_el': row.get('date_creation') or datetime.now(),
                }
            )

        # 3. Migrar pólizas
        self.stdout.write('Migrando pólizas...')
        from polizas.models import Poliza
        cursor.execute('SELECT * FROM projet_projetosis')
        for row in cursor.fetchall():
            Poliza.objects.update_or_create(
                recu=row['recu'],
                defaults={
                    'fecha_hoy': row.get('fecha_hoy'),
                    'letype': row.get('letype', ''),
                    'attestation': row.get('attestation', ''),
                    'police': row.get('police', ''),
                    'marque': row.get('marque', ''),
                    'matricule': row.get('matricule', ''),
                    'produit': row.get('produit', ''),
                    'designation': row.get('designation', ''),
                    'assure': row.get('assure', ''),
                    'du': row.get('du'),
                    'au': row.get('au'),
                    'espece': float(row.get('espece', 0) or 0),
                    'cheque': float(row.get('cheque', 0) or 0),
                    'virement': float(row.get('virement', 0) or 0),
                    'totale': float(row.get('totale', 0) or 0),
                    'reste': float(row.get('reste', 0) or 0),
                    'client_id': row.get('client_id'),
                }
            )

        # 4. Migrar siniestros
        self.stdout.write('Migrando siniestros...')
        from siniestros.models import Sinistro
        cursor.execute('SELECT * FROM table_sinistres')
        for row in cursor.fetchall():
            Sinistro.objects.update_or_create(
                id=row['id'],
                defaults={
                    'ref_sinistre': row.get('ref_sinistre', ''),
                    'date_survenance': row.get('date_survenance'),
                    'description': row.get('description', ''),
                    'poliza_id': row.get('recu'),
                    'creado_el': row.get('date_creation') or datetime.now(),
                }
            )

        # 5. Migrar garantías
        self.stdout.write('Migrando garantías...')
        from garantias.models import Garantia, GarantiaOption, GarantiaFranchise
        cursor.execute('SELECT * FROM garanties')
        for row in cursor.fetchall():
            Garantia.objects.update_or_create(
                id=row['id_garantie'],
                defaults={
                    'nom_garantie': row.get('nom_garantie', ''),
                    'has_configuration': bool(row.get('has_configuration', False)),
                }
            )

        # 6. Migrar opciones de garantías
        self.stdout.write('Migrando opciones...')
        cursor.execute('SELECT * FROM garanties_options')
        for row in cursor.fetchall():
            GarantiaOption.objects.update_or_create(
                id=row['id'],
                defaults={
                    'garantia_id': row.get('garantie_id'),
                    'nom_option': row.get('nom_option', ''),
                }
            )

        # 7. Migrar franquicias
        self.stdout.write('Migrando franquicias...')
        cursor.execute('SELECT * FROM garanties_franchises')
        for row in cursor.fetchall():
            GarantiaFranchise.objects.update_or_create(
                id=row['id'],
                defaults={
                    'garantia_id': row.get('garantie_id'),
                    'nom_franchise': row.get('nom_franchise', ''),
                }
            )

        # 8. Migrar tipos de documento
        self.stdout.write('Migrando tipos de documento...')
        from documentos.models import TipoDocumento
        cursor.execute('SELECT * FROM type_attestation')
        for row in cursor.fetchall():
            TipoDocumento.objects.update_or_create(
                id=row['id'],
                defaults={
                    'tipo_documento': row.get('tipo_documento', ''),
                }
            )

        # 9. Migrar expertos
        self.stdout.write('Migrando expertos...')
        from expertos.models import Experto
        cursor.execute('SELECT * FROM experts')
        for row in cursor.fetchall():
            Experto.objects.update_or_create(
                id=row['id'],
                defaults={
                    'nom_expert': row.get('nom_expert', ''),
                }
            )

        # 10. Migrar banco
        self.stdout.write('Migrando bancos...')
        from banco.models import Banco, Benificiario, EnvioBanco
        cursor.execute('SELECT * FROM banque')
        for row in cursor.fetchall():
            Banco.objects.update_or_create(
                id=row['id'],
                defaults={
                    'nom_banque': row.get('nom_banque', ''),
                }
            )

        cursor.execute('SELECT * FROM benificiare')
        for row in cursor.fetchall():
            Benificiario.objects.update_or_create(
                id=row['id'],
                defaults={
                    'nom_benificiare': row.get('nom_benificiare', ''),
                    'poliza_id': row.get('recu'),
                }
            )

        cursor.execute('SELECT * FROM les_envoies')
        for row in cursor.fetchall():
            EnvioBanco.objects.update_or_create(
                id=row['id'],
                defaults={
                    'banco_id': row.get('banque_id'),
                    'poliza_id': row.get('recu'),
                    'montant': float(row.get('montant', 0) or 0),
                    'fecha_envio': row.get('fecha_envio'),
                }
            )

        # 11. Migrar courrier
        self.stdout.write('Migrando courriers...')
        from courrier.models import EnvioCourrier
        cursor.execute('SELECT * FROM envoie_courrier')
        for row in cursor.fetchall():
            EnvioCourrier.objects.update_or_create(
                id=row['id'],
                defaults={
                    'poliza_id': row.get('recu'),
                    'destinataire': row.get('destinataire', ''),
                    'fecha_envio': row.get('fecha_envio'),
                }
            )

        conn.close()
        self.stdout.write(self.style.SUCCESS('Migración completada con éxito.'))
