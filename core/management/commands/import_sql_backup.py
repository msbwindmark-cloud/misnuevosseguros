import re
import sys
from decimal import Decimal
from datetime import datetime, date
from django.core.management.base import BaseCommand
from django.utils import timezone

def parse_mysql_value(val):
    val = val.strip()
    if val == '' or val == 'NULL':
        return None
    if val.startswith('"') and val.endswith('"'):
        inner = val[1:-1]
        inner = inner.replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
        return inner
    if val.startswith("'") and val.endswith("'"):
        inner = val[1:-1]
        inner = inner.replace("\\'", "'").replace('\\\\', '\\')
        return inner
    return val

def parse_mysql_row(row_text):
    values = []
    current = ''
    in_quotes = False
    quote_char = None
    escape_next = False
    for c in row_text:
        if escape_next:
            current += c
            escape_next = False
            continue
        if c == '\\':
            current += c
            escape_next = True
            continue
        if c in ('"', "'"):
            if not in_quotes:
                in_quotes = True
                quote_char = c
            elif c == quote_char:
                in_quotes = False
                quote_char = None
            current += c
            continue
        if c == ',' and not in_quotes:
            values.append(parse_mysql_value(current))
            current = ''
            continue
        current += c
    values.append(parse_mysql_value(current))
    return values

def extract_inserts(content):
    inserts = []
    idx = 0
    while True:
        insert_pos = content.find('INSERT INTO ', idx)
        if insert_pos == -1:
            break
        rest = content[insert_pos + 12:]
        m = re.match(r'(\w+)\s+VALUES\s*', rest)
        if not m:
            idx = insert_pos + 12
            continue
        table_name = m.group(1)
        values_start = insert_pos + 12 + m.end()
        paren_depth = 0
        in_str = False
        str_char = None
        escape = False
        end_pos = None
        for i, c in enumerate(content[values_start:], start=values_start):
            if escape:
                escape = False
                continue
            if c == '\\':
                escape = True
                continue
            if c in ('"', "'"):
                if not in_str:
                    in_str = True
                    str_char = c
                elif c == str_char:
                    in_str = False
                    str_char = None
                continue
            if in_str:
                continue
            if c == '(':
                paren_depth += 1
            elif c == ')':
                paren_depth -= 1
            elif c == ';' and paren_depth == 0:
                end_pos = i
                break
        if end_pos:
            values_block = content[values_start:end_pos].strip()
            if values_block.endswith(';'):
                values_block = values_block[:-1]
            while values_block.endswith(','):
                values_block = values_block[:-1]
            inserts.append((table_name, values_block))
            idx = end_pos + 1
        else:
            idx = values_start + 1
    return inserts

def to_date(val):
    if not val:
        return None
    val = val.strip('"').strip("'")
    if not val or val == '0000-00-00' or val == '0000-00-00 00:00:00':
        return None
    for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f'):
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            continue
    return None

def to_decimal(val):
    if val is None:
        return None
    if isinstance(val, str):
        val = val.strip()
        if val == '' or val == '0':
            return Decimal('0.00')
        return Decimal(val)
    return Decimal(str(val))

class Command(BaseCommand):
    help = 'Import data from MySQL SQL backup into Django models'

    def add_arguments(self, parser):
        parser.add_argument('sql_file', nargs='?',
                            default='db-backup-2026-07-08_19-42-28.sql',
                            help='Path to SQL backup file')

    SKIP_TABLES = {
        'annee_d_assurance', 'annee_d_assurance_chiffre', 'assistance',
        'banner', 'brie_de_glaces', 'caroussel_slider', 'country_state_city',
        'defense_et_recours', 'dommages_collision', 'dommages_tous_accidents',
        'facturas', 'folders', 'franchise_0_vip_valeur_a_neuf',
        'franchise_0_vip_valeur_venale', 'franchise_10_valeur_a_neuf',
        'franchise_10_valeur_venale', 'franchise_15_valeur_a_neuf',
        'franchise_15_valeur_venale', 'franchise_20_valeur_a_neuf',
        'franchise_20_valeur_venale', 'franchise_3_valeur_a_neuf',
        'franchise_3_valeur_venale', 'franchise_5_valeur_a_neuf',
        'franchise_5_valeur_venale', 'garantie_franchises',
        'garantie_option_values', 'garantie_options', 'garanties',
        'incendie', 'incendie_chiffre', 'les_clients',
        'letype', 'person', 'pr', 'protection_conducteur_trice',
        'protection_passagers', 'proyectosis_copie', 'releves',
        'responsabilite_civile', 'sinistre', 'sinistre_chiffre',
        'tarif_actualise', 'tbl_categories', 'treeview_items',
        'users', 'usuarios', 'usuarios2', 'usuarios_eliminados',
        'valeur_a_neuf', 'valeur_venale', 'vol', 'vol_chiffre',
        'proyectosis_eliminados', 'proyectosis_copia',
    }

    def handle(self, *args, **options):
        sql_path = options['sql_file']
        self.stdout.write(f"Reading {sql_path}...")
        with open(sql_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        inserts = extract_inserts(content)
        self.stdout.write(f"Found {len(inserts)} INSERT statements")

        # Disable FK checks for the import, then re-enable
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = OFF;")

        from clientes.models import Cliente
        from polizas.models import Poliza, PolizaEliminada, PolizaGarantia, PolizaGarantiaOption, PolizaGarantiaFranchise
        from siniestros.models import Sinistro, DocumentoSinistro, Formule, ReferenceReglement, DocumentDeBase
        from garantias.models import Garantia, GarantiaOption
        from banco.models import Banco, Benificiario, EnvioBanco
        from courrier.models import Destinataire, Expediteur, EnvioCourrier
        from documentos.models import TipoDocumento, DocumentoUsuario
        from expertos.models import Experto
        from attestations.models import TypeAttestation, Attestation

        self.TypeAttestation = TypeAttestation
        self.Attestation = Attestation
        self.Banco = Banco
        self.Benificiario = Benificiario
        self.Destinataire = Destinataire
        self.DocumentDeBase = DocumentDeBase
        self.DocumentoSinistro = DocumentoSinistro
        self.DocumentoUsuario = DocumentoUsuario
        self.EnvioCourrier = EnvioCourrier
        self.Expediteur = Expediteur
        self.Experto = Experto
        self.Formule = Formule
        self.EnvioBanco = EnvioBanco
        self.Cliente = Cliente
        self.Poliza = Poliza
        self.PolizaEliminada = PolizaEliminada
        self.PolizaGarantia = PolizaGarantia
        self.PolizaGarantiaOption = PolizaGarantiaOption
        self.PolizaGarantiaFranchise = PolizaGarantiaFranchise
        self.ReferenceReglement = ReferenceReglement
        self.Sinistro = Sinistro
        self.TipoDocumento = TipoDocumento
        self.Garantia = Garantia
        self.GarantiaOption = GarantiaOption

        for table_name, values_block in inserts:
            if table_name in self.SKIP_TABLES:
                continue
            handler = getattr(self, f'import_{table_name}', None)
            if handler:
                try:
                    count = handler(values_block)
                    self.stdout.write(f"  {table_name}: {count} rows")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  {table_name}: ERROR - {e}"))
            else:
                self.stdout.write(self.style.WARNING(f"  {table_name}: no handler, skipping"))

        # Re-enable FK checks
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = ON;")

    def _parse_values(self, values_block):
        rows = []
        paren_depth = 0
        current = ''
        in_str = False
        str_char = None
        escape = False
        for c in values_block:
            if escape:
                current += c
                escape = False
                continue
            if c == '\\':
                current += c
                escape = True
                continue
            if c in ('"', "'"):
                current += c
                if not in_str:
                    in_str = True
                    str_char = c
                elif c == str_char:
                    in_str = False
                    str_char = None
                continue
            if in_str:
                current += c
                continue
            if c == '(':
                if paren_depth > 0:
                    current += c
                paren_depth += 1
            elif c == ')':
                paren_depth -= 1
                if paren_depth == 0:
                    rows.append(current.strip())
                    current = ''
                else:
                    current += c
            elif c == ',' and paren_depth == 1:
                current += c
            else:
                if paren_depth >= 1:
                    current += c
        return [parse_mysql_row(r) for r in rows if r]

    def import_type_attestation(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            objs.append(self.TypeAttestation(
                id=int(r[0]),
                type_attestation=r[1],
            ))
        self.TypeAttestation.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_attestation(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            objs.append(self.Attestation(
                id=int(r[0]),
                id_type_attestation_id=int(r[1]) if r[1] else None,
                numero_attestation=r[2] or '',
                seleccionado=bool(int(r[3])) if r[3] else True,
            ))
        self.Attestation.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_banque(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            objs.append(self.Banco(
                id=int(r[0]),
                nom_banque=r[1] or '',
                compte_banque=r[2] or '',
                address_banque=r[4] or '',
                distrit_banque=r[5] or '',
                ville_banque=r[6] or '',
            ))
        self.Banco.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_benificiare(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            objs.append(self.Benificiario(
                id=int(r[0]),
                nom_benificiaire=r[1] or '',
                banque_benificiaire=r[2] or '',
                compte_benificiaire=r[3] or '',
            ))
        self.Benificiario.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_destinataire(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            objs.append(self.Destinataire(
                id=int(r[0]),
                nom_destinataire=r[1] or '',
                adresse_destinataire=r[2] or '',
            ))
        self.Destinataire.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_document_de_base(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            objs.append(self.DocumentDeBase(
                id=int(r[0]),
                nom_document_de_base=r[1] or '',
            ))
        self.DocumentDeBase.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_documentos_sinistres(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            objs.append(self.DocumentoSinistro(
                id=int(r[0]),
                code_sinistre=r[1] or '',
                nombre_archivo=r[2] or '',
                tipo_documento=int(r[3]) if r[3] else None,
                ruta_archivo=r[4] or '',
                id_documento_usuario_origen=int(r[5]) if r[5] else None,
            ))
        self.DocumentoSinistro.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_documentos_usuarios(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            tipo_doc_id = int(r[5]) if len(r) > 5 and r[5] else None
            if tipo_doc_id and not self.TipoDocumento.objects.filter(id=tipo_doc_id).exists():
                tipo_doc_id = None
            objs.append(self.DocumentoUsuario(
                id=int(r[0]),
                tipo_documento_usuario=r[1] or '',
                nombre_documento_usuario=r[2] or '',
                tamanio_documento_usuario=int(r[3]) if r[3] else None,
                id_usuario=int(r[4]) if r[4] else 0,
                tipo_documento_id=tipo_doc_id,
            ))
        self.DocumentoUsuario.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_envoie_courrier(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            objs.append(self.EnvioCourrier(
                id=int(r[0]),
                date_envoie_courrier=to_date(r[1]) or date.today(),
                expediteur_envoie_courrier=r[2] or '',
                destinataire_envoie_courrier=r[4] or '',
                addresse_envoie_courrier=r[5] or '',
                tipo_documento_envoie_courrier=r[6] if len(r) > 6 else None,
                nombre_documento_envoie_courrier=r[7] if len(r) > 7 else None,
                tamanio_documento_envoie_courrier=int(r[8]) if len(r) > 8 and r[8] else None,
            ))
        self.EnvioCourrier.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_expediteur(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            objs.append(self.Expediteur(
                id=int(r[0]),
                nom_expediteur=r[1] or '',
                adresse_expediteur=r[2] or '',
            ))
        self.Expediteur.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_experts(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            objs.append(self.Experto(
                id=int(r[0]),
                nom_expert=r[1] or '',
            ))
        self.Experto.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_formule(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            objs.append(self.Formule(
                id=int(r[0]),
                nom_formule=r[1] or '',
            ))
        self.Formule.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_les_envoies(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            # r[8] = id_benificiaire, r[9] = id_banque
            ben_id = int(r[8]) if len(r) > 8 and r[8] else None
            ban_id = int(r[9]) if len(r) > 9 and r[9] else None
            if ben_id and not self.Benificiario.objects.filter(id=ben_id).exists():
                ben_id = None
            if ban_id and not self.Banco.objects.filter(id=ban_id).exists():
                ban_id = None
            objs.append(self.EnvioBanco(
                id=int(r[0]),
                nom_envoie=r[1] or '',
                banque_envoie=r[2] or '',
                compte_envoie=r[3] or '',
                date_envoie=to_date(r[4]),
                montant_envoie=to_decimal(r[5]) or Decimal('0.00'),
                motif_envoie=r[6] or '',
                benificiario_id=ben_id,
                banco_id=ban_id,
            ))
        self.EnvioBanco.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_liste_des_clients(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            objs.append(self.Cliente(
                id=int(r[0]),
                code_client=int(r[1]) if r[1] else 0,
                nom_client=r[2] or '',
                telephone_client=r[3] or '',
                email_client=r[4] or '',
            ))
        self.Cliente.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_proyectosis(self, values_block):
        rows = self._parse_values(values_block)
        self.stdout.write(f"    Parsed {len(rows)} rows from SQL")
        if rows:
            self.stdout.write(f"    First row: {len(rows[0])} values, sample: {rows[0][:5]}")
        objs = []
        for r in rows:
            du_date = to_date(r[12])
            au_date = to_date(r[13])
            date_vers = to_date(r[23])
            objs.append(self.Poliza(
                recu=int(r[0]),
                fecha_hoy=to_date(r[1]),
                letype=r[2] or 'Affaire nouvelle',
                attestation=r[3] or '',
                police=r[4] or '',
                marque=r[5] or '',
                designation=r[6] or '',
                matricule=r[7] or '',
                produit=r[8] or '',
                assure=r[9] or '',
                code_client=str(r[10]) if r[10] else '',
                prenom=r[11] or '',
                du=du_date or date.today(),
                au=au_date or date.today(),
                prime_net=to_decimal(r[14]) or Decimal('0.00'),
                taxes=to_decimal(r[15]) or Decimal('0.00'),
                tp=to_decimal(r[16]) or Decimal('0.00'),
                accesoires=to_decimal(r[17]) or Decimal('0.00'),
                totale=to_decimal(r[18]) or Decimal('0.00'),
                espece=to_decimal(r[19]) or Decimal('0.00'),
                cheque=to_decimal(r[20]) or Decimal('0.00'),
                virement=to_decimal(r[21]) or Decimal('0.00'),
                reste=to_decimal(r[22]) or Decimal('0.00'),
                date_versement=date_vers,
                mode_paiment=r[24] or 'nulo',
                telefono=r[26] if len(r) > 26 and r[26] else '',
                email=r[27] if len(r) > 27 and r[27] else '',
                address_client=r[28] if len(r) > 28 and r[28] else '',
            ))
        self.Poliza.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_proyectosis_elimines(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            du_date = to_date(r[9])
            au_date = to_date(r[10])
            date_vers = to_date(r[16])
            objs.append(self.PolizaEliminada(
                recu=int(r[0]),
                fecha_hoy=to_date(r[1]),
                letype=r[2] or '',
                attestation=r[3] or '',
                police=r[4] or '',
                matricule=r[5] or '',
                produit=r[6] or '',
                assure=r[7] or '',
                du=du_date or date.today(),
                au=au_date or date.today(),
                totale=to_decimal(r[11]) or Decimal('0.00'),
                espece=to_decimal(r[12]) or Decimal('0.00'),
                cheque=to_decimal(r[13]) or Decimal('0.00'),
                virement=to_decimal(r[14]) or Decimal('0.00'),
                reste=to_decimal(r[15]) or Decimal('0.00'),
                date_versement=date_vers,
                mode_paiment=r[17] or 'nulo',
                cree_le=to_date(r[18]) or timezone.now(),
            ))
        self.PolizaEliminada.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_proyectosis_garantie(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            recu_val = int(r[0])
            garantia_id = int(r[1])
            if not self.Poliza.objects.filter(recu=recu_val).exists():
                continue
            if not self.Garantia.objects.filter(id=garantia_id).exists():
                continue
            objs.append(self.PolizaGarantia(
                poliza_id=recu_val,
                garantia_id=garantia_id,
                valeur=to_decimal(r[2]) if r[2] else None,
            ))
        self.PolizaGarantia.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_proyectosis_garantie_options(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            recu_val = int(r[0])
            garantia_id = int(r[1])
            option_id = int(r[2])
            if not self.Poliza.objects.filter(recu=recu_val).exists():
                continue
            if not self.Garantia.objects.filter(id=garantia_id).exists():
                continue
            if not self.GarantiaOption.objects.filter(id=option_id).exists():
                continue
            objs.append(self.PolizaGarantiaOption(
                poliza_id=recu_val,
                garantia_id=garantia_id,
                option_id=option_id,
                valeur=to_decimal(r[3]) if r[3] else None,
            ))
        self.PolizaGarantiaOption.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_proyectosis_garantie_franchises(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            recu_val = int(r[0])
            garantia_id = int(r[1])
            option_id = int(r[2])
            franchise_id = int(r[3])
            if not self.Poliza.objects.filter(recu=recu_val).exists():
                continue
            if not self.Garantia.objects.filter(id=garantia_id).exists():
                continue
            if not self.GarantiaOption.objects.filter(id=option_id).exists():
                continue
            objs.append(self.PolizaGarantiaFranchise(
                poliza_id=recu_val,
                garantia_id=garantia_id,
                option_id=option_id,
                franchise_id=franchise_id,
                montant_franchise=to_decimal(r[4]) if r[4] else None,
            ))
        self.PolizaGarantiaFranchise.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_reference_reglement(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            objs.append(self.ReferenceReglement(
                id=int(r[0]),
                nom_reference_reglement=r[1] or '',
            ))
        self.ReferenceReglement.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_table_sinistres(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            poliza_id = int(r[20]) if len(r) > 20 and r[20] else None
            if poliza_id and not self.Poliza.objects.filter(recu=poliza_id).exists():
                poliza_id = None
            objs.append(self.Sinistro(
                id=int(r[0]),
                code_sinistre=r[1] or '',
                ref_sinistre=r[2] or '',
                date_operation=to_date(r[3]) or date.today(),
                date_sinistre=to_date(r[4]) or date.today(),
                date_reception=to_date(r[5]) or date.today(),
                police=r[6] or '',
                nom_formule=r[7] or '',
                assure=r[8] or '',
                categorie_assurance=r[9] or '',
                reference_assurance=r[10] or '',
                benificiaire=r[11] or '',
                reference_assistance=r[12] if len(r) > 12 else None,
                nom_expert=r[13] if len(r) > 13 else None,
                reference_reglement=r[14] or '',
                document_de_base=r[15] if len(r) > 15 else None,
                reference_payement=r[16] if len(r) > 16 else None,
                montant=to_decimal(r[17]) if r[17] else None,
                date_payement=to_date(r[18]),
                poliza_id=poliza_id,
                cod_sig_correcto=bool(int(r[21])) if len(r) > 21 and r[21] else False,
            ))
        self.Sinistro.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)

    def import_tipo_documentos(self, values_block):
        rows = self._parse_values(values_block)
        objs = []
        for r in rows:
            objs.append(self.TipoDocumento(
                id=int(r[0]),
                tipo_documento=r[1] or '',
            ))
        self.TipoDocumento.objects.bulk_create(objs, ignore_conflicts=True)
        return len(objs)
