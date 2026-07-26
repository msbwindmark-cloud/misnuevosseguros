"""
Standalone script to populate the Django database from the MySQL SQL backup.
Run from any terminal: python populate_db.py

It configures Django, disables FK checks, imports data, seeds garantias,
copies the SQL backup from Downloads if needed, and re-enables FK checks.
"""

import os
import sys
import re
from decimal import Decimal
from datetime import datetime, date

# ── 1. Django setup ──────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()
from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone

# ── 2. Locate the SQL backup ────────────────────────────────────────────────
DEFAULT_SQL = os.path.join(BASE_DIR, 'db-backup-2026-07-25_15-02-15.sql')
DOWNLOAD_SQL = os.path.expanduser(
    '~/Downloads/db-backup-2026-07-25_15-02-15.sql'
)

SQL_PATH = DEFAULT_SQL
if not os.path.exists(SQL_PATH):
    alt = os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads',
                       'db-backup-2026-07-25_15-02-15.sql')
    if os.path.exists(alt):
        SQL_PATH = alt
    elif os.path.exists(DOWNLOAD_SQL):
        SQL_PATH = DOWNLOAD_SQL

# ── 3. Utility functions ────────────────────────────────────────────────────

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

def _parse_values(values_block):
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

# ── 4. Tables to skip (already seeded or not needed) ────────────────────────
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

# ── 5. Main import logic ────────────────────────────────────────────────────

def run():
    print(f"Reading {SQL_PATH}...")
    with open(SQL_PATH, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    inserts = extract_inserts(content)
    print(f"Found {len(inserts)} INSERT statements")

    # Disable FK checks
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys = OFF;")
    print("FK checks disabled")

    # ── Clear existing data for a full refresh ──
    print("Clearing existing data...")
    from clientes.models import Cliente
    from polizas.models import Poliza, PolizaEliminada, PolizaGarantia, PolizaGarantiaOption, PolizaGarantiaFranchise
    from siniestros.models import Sinistro, DocumentoSinistro, Formule, ReferenceReglement, DocumentDeBase
    from garantias.models import Garantia, GarantiaOption, GarantiaFranchise
    from banco.models import Banco, Benificiario, EnvioBanco
    from courrier.models import Destinataire, Expediteur, EnvioCourrier
    from documentos.models import TipoDocumento, DocumentoUsuario
    from expertos.models import Experto
    from attestations.models import TypeAttestation, Attestation

    # Tables that get populated from the SQL dump (delete in FK-safe order)
    tables_to_clear = [
        PolizaGarantiaFranchise, PolizaGarantiaOption, PolizaGarantia,
        DocumentoSinistro, Sinistro, EnvioBanco, EnvioCourrier,
        PolizaEliminada, Poliza, Attestation, Benificiario,
        DocumentoUsuario, Cliente, Banco, Destinataire, Expediteur,
        Experto, TipoDocumento, Formule, DocumentDeBase,
        ReferenceReglement, TypeAttestation,
    ]
    for model in tables_to_clear:
        model.objects.all().delete()
    print("Existing data cleared")

    # ── Seed garantias if empty ──
    if Garantia.objects.count() == 0:
        print("Seeding garantias...")
        Garantia.objects.bulk_create([
            Garantia(id=1, nom_garantie='responsabilite_civile', has_configuration=False),
            Garantia(id=2, nom_garantie='defense_et_recours', has_configuration=False),
            Garantia(id=7, nom_garantie='VOL', has_configuration=False),
            Garantia(id=8, nom_garantie='incendie', has_configuration=False),
            Garantia(id=9, nom_garantie='dommages_collision', has_configuration=True),
            Garantia(id=10, nom_garantie='dommages_tous_accidents', has_configuration=True),
            Garantia(id=13, nom_garantie='bris_de_glaces', has_configuration=True),
            Garantia(id=14, nom_garantie='protection_passagers', has_configuration=True),
            Garantia(id=17, nom_garantie='protection_conducteur_trice', has_configuration=True),
            Garantia(id=19, nom_garantie='assistance', has_configuration=True),
        ])
        GarantiaOption.objects.bulk_create([
            GarantiaOption(id=1, garantia_id=10, nom_option='Valeur vénale', requires_montant=False),
            GarantiaOption(id=2, garantia_id=10, nom_option='Valeur à neuf', requires_montant=False),
            GarantiaOption(id=3, garantia_id=13, nom_option="Année d'assurance", requires_montant=True),
            GarantiaOption(id=4, garantia_id=13, nom_option='sinistre', requires_montant=True),
            GarantiaOption(id=5, garantia_id=14, nom_option='20000 - 20000 - 2000', requires_montant=False),
            GarantiaOption(id=6, garantia_id=14, nom_option='40000 - 40000 - 4000', requires_montant=False),
            GarantiaOption(id=7, garantia_id=14, nom_option='60000 - 60000 - 6000', requires_montant=False),
            GarantiaOption(id=8, garantia_id=14, nom_option='70000 - 70000 - 7000', requires_montant=False),
            GarantiaOption(id=9, garantia_id=14, nom_option='80000 - 80000 - 8000', requires_montant=False),
            GarantiaOption(id=10, garantia_id=14, nom_option='90000 - 90000 - 9000', requires_montant=False),
            GarantiaOption(id=11, garantia_id=14, nom_option='100000 - 100000 - 10000', requires_montant=False),
            GarantiaOption(id=12, garantia_id=14, nom_option='110000 - 110000 - 11000', requires_montant=False),
            GarantiaOption(id=13, garantia_id=14, nom_option='120000 - 120000 - 12000', requires_montant=False),
            GarantiaOption(id=14, garantia_id=14, nom_option='150000 - 150000 - 15000', requires_montant=False),
            GarantiaOption(id=15, garantia_id=14, nom_option='200000 - 200000 - 20000', requires_montant=False),
            GarantiaOption(id=16, garantia_id=14, nom_option='10000 - 10000 - 1000', requires_montant=False),
            GarantiaOption(id=17, garantia_id=17, nom_option='50000 / 50000 / 5000', requires_montant=False),
            GarantiaOption(id=18, garantia_id=17, nom_option='60000 / 60000 / 6000', requires_montant=False),
            GarantiaOption(id=19, garantia_id=17, nom_option='70000 / 70000 / 7000', requires_montant=False),
            GarantiaOption(id=20, garantia_id=17, nom_option='100000 / 100000 / 10000', requires_montant=False),
            GarantiaOption(id=21, garantia_id=17, nom_option='200000 / 200000 / 20000', requires_montant=False),
            GarantiaOption(id=22, garantia_id=19, nom_option='HANI', requires_montant=False),
            GarantiaOption(id=23, garantia_id=19, nom_option='IMTIAZ', requires_montant=False),
            GarantiaOption(id=24, garantia_id=19, nom_option='KAMEL', requires_montant=False),
            GarantiaOption(id=25, garantia_id=19, nom_option='KAMEL MAKMOUL', requires_montant=False),
            GarantiaOption(id=26, garantia_id=9, nom_option='10000 (Fr. 1000): 10000', requires_montant=False),
            GarantiaOption(id=27, garantia_id=9, nom_option='20000 (Fr. 1000): 20000', requires_montant=False),
            GarantiaOption(id=28, garantia_id=9, nom_option='30000 (Fr. 1000): 30000', requires_montant=False),
            GarantiaOption(id=29, garantia_id=9, nom_option='40000 (Fr. 1000): 40000', requires_montant=False),
            GarantiaOption(id=30, garantia_id=9, nom_option='50000 (Fr. 1000): 50000', requires_montant=False),
            GarantiaOption(id=31, garantia_id=9, nom_option='10000 (Fr. 5% Min 1000): 10000', requires_montant=False),
            GarantiaOption(id=32, garantia_id=9, nom_option='20000 (Fr. 5% Min 1000): 20000', requires_montant=False),
            GarantiaOption(id=33, garantia_id=9, nom_option='30000 (Fr. 5% Min 1000): 30000', requires_montant=False),
            GarantiaOption(id=34, garantia_id=9, nom_option='40000 (Fr. 5% Min 1000): 40000', requires_montant=False),
            GarantiaOption(id=35, garantia_id=9, nom_option='50000 (Fr. 5% Min 1000): 50000', requires_montant=False),
            GarantiaOption(id=36, garantia_id=9, nom_option='60000 (Fr. 5% Min 1000): 60000', requires_montant=False),
            GarantiaOption(id=37, garantia_id=9, nom_option='70000 (Fr. 5% Min 1000): 70000', requires_montant=False),
            GarantiaOption(id=38, garantia_id=9, nom_option='80000 (Fr. 5% Min 1000): 80000', requires_montant=False),
            GarantiaOption(id=39, garantia_id=9, nom_option='90000 (Fr. 5% Min 1000): 90000', requires_montant=False),
            GarantiaOption(id=40, garantia_id=9, nom_option='100000 (Fr. 5% Min 1000): 100000', requires_montant=False),
            GarantiaOption(id=41, garantia_id=9, nom_option='Déplafonée (Fr. 5% Min 1000):', requires_montant=False),
        ])
        GarantiaFranchise.objects.bulk_create([
            GarantiaFranchise(id=1, option_id=1, nom_franchise='Franchise 0% VIP'),
            GarantiaFranchise(id=2, option_id=1, nom_franchise='Franchise 3%'),
            GarantiaFranchise(id=3, option_id=1, nom_franchise='Franchise 5%'),
            GarantiaFranchise(id=4, option_id=1, nom_franchise='Franchise 10%'),
            GarantiaFranchise(id=5, option_id=1, nom_franchise='Franchise 15%'),
            GarantiaFranchise(id=6, option_id=1, nom_franchise='Franchise 20%'),
            GarantiaFranchise(id=7, option_id=2, nom_franchise='Franchise 0% VIP'),
            GarantiaFranchise(id=8, option_id=2, nom_franchise='Franchise 3%'),
            GarantiaFranchise(id=9, option_id=2, nom_franchise='Franchise 5%'),
            GarantiaFranchise(id=10, option_id=2, nom_franchise='Franchise 10%'),
            GarantiaFranchise(id=11, option_id=2, nom_franchise='Franchise 15%'),
            GarantiaFranchise(id=12, option_id=2, nom_franchise='Franchise 20%'),
        ])
        print("Garantias seeded: 10 garantias, 41 options, 12 franchises")

    # ── Process each table ──
    for table_name, values_block in inserts:
        if table_name in SKIP_TABLES:
            continue

        rows = _parse_values(values_block)

        if table_name == 'type_attestation':
            TypeAttestation.objects.bulk_create(
                [TypeAttestation(id=int(r[0]), type_attestation=r[1]) for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'attestation':
            Attestation.objects.bulk_create(
                [Attestation(id=int(r[0]), id_type_attestation_id=int(r[1]) if r[1] else None,
                             numero_attestation=r[2] or '', seleccionado=bool(int(r[3])) if r[3] else True)
                 for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'banque':
            Banco.objects.bulk_create(
                [Banco(id=int(r[0]), nom_banque=r[1] or '', compte_banque=r[2] or '',
                       address_banque=r[4] or '', distrit_banque=r[5] or '', ville_banque=r[6] or '')
                 for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'benificiare':
            Benificiario.objects.bulk_create(
                [Benificiario(id=int(r[0]), nom_benificiaire=r[1] or '',
                              banque_benificiaire=r[2] or '', compte_benificiaire=r[3] or '')
                 for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'destinataire':
            Destinataire.objects.bulk_create(
                [Destinataire(id=int(r[0]), nom_destinataire=r[1] or '',
                              adresse_destinataire=r[2] or '') for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'document_de_base':
            DocumentDeBase.objects.bulk_create(
                [DocumentDeBase(id=int(r[0]), nom_document_de_base=r[1] or '') for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'documentos_sinistres':
            DocumentoSinistro.objects.bulk_create(
                [DocumentoSinistro(id=int(r[0]), code_sinistre=r[1] or '', nombre_archivo=r[2] or '',
                                   tipo_documento=int(r[3]) if r[3] else None,
                                   ruta_archivo=r[4] or '',
                                   id_documento_usuario_origen=int(r[5]) if r[5] else None)
                 for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'documentos_usuarios':
            DocumentoUsuario.objects.bulk_create(
                [DocumentoUsuario(id=int(r[0]), tipo_documento_usuario=r[1] or '',
                                  nombre_documento_usuario=r[2] or '',
                                  tamanio_documento_usuario=int(r[3]) if r[3] else None,
                                  id_usuario=int(r[4]) if r[4] else 0,
                                  tipo_documento_id=int(r[5]) if len(r) > 5 and r[5] else None)
                 for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'envoie_courrier':
            EnvioCourrier.objects.bulk_create(
                [EnvioCourrier(id=int(r[0]), date_envoie_courrier=to_date(r[1]) or date.today(),
                               expediteur_envoie_courrier=r[2] or '',
                               destinataire_envoie_courrier=r[4] or '',
                               addresse_envoie_courrier=r[5] or '',
                               tipo_documento_envoie_courrier=r[6] if len(r) > 6 else None,
                               nombre_documento_envoie_courrier=r[7] if len(r) > 7 else None,
                               tamanio_documento_envoie_courrier=int(r[8]) if len(r) > 8 and r[8] else None)
                 for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'expediteur':
            Expediteur.objects.bulk_create(
                [Expediteur(id=int(r[0]), nom_expediteur=r[1] or '',
                            adresse_expediteur=r[2] or '') for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'experts':
            Experto.objects.bulk_create(
                [Experto(id=int(r[0]), nom_expert=r[1] or '') for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'formule':
            Formule.objects.bulk_create(
                [Formule(id=int(r[0]), nom_formule=r[1] or '') for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'les_envoies':
            EnvioBanco.objects.bulk_create(
                [EnvioBanco(id=int(r[0]), nom_envoie=r[1] or '', banque_envoie=r[2] or '',
                            compte_envoie=r[3] or '', date_envoie=to_date(r[4]),
                            montant_envoie=to_decimal(r[5]) or Decimal('0.00'),
                            motif_envoie=r[6] or '',
                            benificiario_id=int(r[8]) if len(r) > 8 and r[8] else None,
                            banco_id=int(r[9]) if len(r) > 9 and r[9] else None)
                 for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'liste_des_clients':
            Cliente.objects.bulk_create(
                [Cliente(id=int(r[0]), code_client=int(r[1]) if r[1] else 0,
                         nom_client=r[2] or '', telephone_client=r[3] or '',
                         email_client=r[4] or '') for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'proyectosis':
            Poliza.objects.bulk_create(
                [Poliza(recu=int(r[0]), fecha_hoy=to_date(r[1]),
                        letype=r[2] or 'Affaire nouvelle', attestation=r[3] or '',
                        police=r[4] or '', marque=r[5] or '', designation=r[6] or '',
                        matricule=r[7] or '', produit=r[8] or '', assure=r[9] or '',
                        code_client=str(r[10]) if r[10] else '', prenom=r[11] or '',
                        du=to_date(r[12]) or date.today(), au=to_date(r[13]) or date.today(),
                        prime_net=to_decimal(r[14]) or Decimal('0.00'),
                        taxes=to_decimal(r[15]) or Decimal('0.00'),
                        tp=to_decimal(r[16]) or Decimal('0.00'),
                        accesoires=to_decimal(r[17]) or Decimal('0.00'),
                        totale=to_decimal(r[18]) or Decimal('0.00'),
                        espece=to_decimal(r[19]) or Decimal('0.00'),
                        cheque=to_decimal(r[20]) or Decimal('0.00'),
                        virement=to_decimal(r[21]) or Decimal('0.00'),
                        reste=to_decimal(r[22]) or Decimal('0.00'),
                        date_versement=to_date(r[23]),
                        mode_paiment=r[24] or 'nulo',
                        telefono=r[26] if len(r) > 26 and r[26] else '',
                        email=r[27] if len(r) > 27 and r[27] else '',
                        address_client=r[28] if len(r) > 28 and r[28] else '')
                 for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'proyectosis_elimines':
            PolizaEliminada.objects.bulk_create(
                [PolizaEliminada(recu=int(r[0]), fecha_hoy=to_date(r[1]),
                                 letype=r[2] or '', attestation=r[3] or '',
                                 police=r[4] or '', matricule=r[5] or '',
                                 produit=r[6] or '', assure=r[7] or '',
                                 du=to_date(r[9]) or date.today(), au=to_date(r[10]) or date.today(),
                                 totale=to_decimal(r[11]) or Decimal('0.00'),
                                 espece=to_decimal(r[12]) or Decimal('0.00'),
                                 cheque=to_decimal(r[13]) or Decimal('0.00'),
                                 virement=to_decimal(r[14]) or Decimal('0.00'),
                                 reste=to_decimal(r[15]) or Decimal('0.00'),
                                 date_versement=to_date(r[16]),
                                 mode_paiment=r[17] or 'nulo',
                                 cree_le=to_date(r[18]) or timezone.now())
                 for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'proyectosis_garantie':
            PolizaGarantia.objects.bulk_create(
                [PolizaGarantia(poliza_id=int(r[0]), garantia_id=int(r[1]),
                                valeur=to_decimal(r[2]) if r[2] else None)
                 for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'proyectosis_garantie_options':
            PolizaGarantiaOption.objects.bulk_create(
                [PolizaGarantiaOption(poliza_id=int(r[0]), garantia_id=int(r[1]),
                                      option_id=int(r[2]), valeur=to_decimal(r[3]) if r[3] else None)
                 for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'proyectosis_garantie_franchises':
            PolizaGarantiaFranchise.objects.bulk_create(
                [PolizaGarantiaFranchise(poliza_id=int(r[0]), garantia_id=int(r[1]),
                                         option_id=int(r[2]), franchise_id=int(r[3]),
                                         montant_franchise=to_decimal(r[4]) if r[4] else None)
                 for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'reference_reglement':
            ReferenceReglement.objects.bulk_create(
                [ReferenceReglement(id=int(r[0]), nom_reference_reglement=r[1] or '') for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'table_sinistres':
            Sinistro.objects.bulk_create(
                [Sinistro(id=int(r[0]), code_sinistre=r[1] or '', ref_sinistre=r[2] or '',
                          date_operation=to_date(r[3]) or date.today(),
                          date_sinistre=to_date(r[4]) or date.today(),
                          date_reception=to_date(r[5]) or date.today(),
                          police=r[6] or '', nom_formule=r[7] or '', assure=r[8] or '',
                          categorie_assurance=r[9] or '', reference_assurance=r[10] or '',
                          benificiaire=r[11] or '',
                          reference_assistance=r[12] if len(r) > 12 else None,
                          nom_expert=r[13] if len(r) > 13 else None,
                          reference_reglement=r[14] or '',
                          document_de_base=r[15] if len(r) > 15 else None,
                          reference_payement=r[16] if len(r) > 16 else None,
                          montant=to_decimal(r[17]) if r[17] else None,
                          date_payement=to_date(r[18]),
                          poliza_id=int(r[20]) if len(r) > 20 and r[20] else None,
                          cod_sig_correcto=bool(int(r[21])) if len(r) > 21 and r[21] else False)
                 for r in rows],
                ignore_conflicts=True
            )
        elif table_name == 'tipo_documentos':
            TipoDocumento.objects.bulk_create(
                [TipoDocumento(id=int(r[0]), tipo_documento=r[1] or '') for r in rows],
                ignore_conflicts=True
            )
        else:
            print(f"  SKIPPED (no handler): {table_name}")
            continue

        print(f"  {table_name}: {len(rows)} rows")

    # Re-enable FK checks
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys = ON;")
    print("FK checks re-enabled")

    # ── Summary ──
    print()
    print("=" * 50)
    print("IMPORT COMPLETE - Summary:")
    print(f"  Clientes:              {Cliente.objects.count()}")
    print(f"  Polizas:               {Poliza.objects.count()}")
    print(f"  Polizas Eliminadas:    {PolizaEliminada.objects.count()}")
    print(f"  PolizaGarantia:        {PolizaGarantia.objects.count()}")
    print(f"  PolizaGarantiaOption:  {PolizaGarantiaOption.objects.count()}")
    print(f"  PolizaGarantiaFranchise:{PolizaGarantiaFranchise.objects.count()}")
    print(f"  Siniestros:            {Sinistro.objects.count()}")
    print(f"  Documentos Sinistro:   {DocumentoSinistro.objects.count()}")
    print(f"  Garantias:             {Garantia.objects.count()}")
    print(f"  Banco:                 {Banco.objects.count()}")
    print(f"  Benificiario:          {Benificiario.objects.count()}")
    print(f"  EnvioBanco:            {EnvioBanco.objects.count()}")
    print(f"  EnvioCourrier:         {EnvioCourrier.objects.count()}")
    print(f"  Destinataire:          {Destinataire.objects.count()}")
    print(f"  Expediteur:            {Expediteur.objects.count()}")
    print(f"  TipoDocumento:         {TipoDocumento.objects.count()}")
    print(f"  DocumentoUsuario:      {DocumentoUsuario.objects.count()}")
    print(f"  Experto:               {Experto.objects.count()}")
    print(f"  TypeAttestation:       {TypeAttestation.objects.count()}")
    print(f"  Attestation:           {Attestation.objects.count()}")
    print(f"  Formule:               {Formule.objects.count()}")
    print(f"  DocumentDeBase:        {DocumentDeBase.objects.count()}")
    print(f"  ReferenceReglement:    {ReferenceReglement.objects.count()}")
    print("=" * 50)


if __name__ == '__main__':
    run()
