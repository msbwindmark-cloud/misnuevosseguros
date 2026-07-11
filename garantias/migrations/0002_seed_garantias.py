from django.db import migrations


def seed_data(apps, schema_editor):
    Garantia = apps.get_model('garantias', 'Garantia')
    GarantiaOption = apps.get_model('garantias', 'GarantiaOption')
    GarantiaFranchise = apps.get_model('garantias', 'GarantiaFranchise')

    # ── Garantias ──
    garantias = [
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
    ]
    Garantia.objects.bulk_create(garantias)

    # ── Options for garantía 10 (dommages_tous_accidents) ──
    opts_10 = [
        GarantiaOption(id=1, garantia_id=10, nom_option='Valeur vénale', requires_montant=False),
        GarantiaOption(id=2, garantia_id=10, nom_option='Valeur à neuf', requires_montant=False),
    ]
    GarantiaOption.objects.bulk_create(opts_10)

    # ── Options for garantía 13 (bris_de_glaces) ──
    opts_13 = [
        GarantiaOption(id=3, garantia_id=13, nom_option="Année d'assurance", requires_montant=True),
        GarantiaOption(id=4, garantia_id=13, nom_option='sinistre', requires_montant=True),
    ]
    GarantiaOption.objects.bulk_create(opts_13)

    # ── Options for garantía 14 (protection_passagers) ──
    opts_14 = [
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
    ]
    GarantiaOption.objects.bulk_create(opts_14)

    # ── Options for garantía 17 (protection_conducteur_trice) ──
    opts_17 = [
        GarantiaOption(id=17, garantia_id=17, nom_option='50000 / 50000 / 5000', requires_montant=False),
        GarantiaOption(id=18, garantia_id=17, nom_option='60000 / 60000 / 6000', requires_montant=False),
        GarantiaOption(id=19, garantia_id=17, nom_option='70000 / 70000 / 7000', requires_montant=False),
        GarantiaOption(id=20, garantia_id=17, nom_option='100000 / 100000 / 10000', requires_montant=False),
        GarantiaOption(id=21, garantia_id=17, nom_option='200000 / 200000 / 20000', requires_montant=False),
    ]
    GarantiaOption.objects.bulk_create(opts_17)

    # ── Options for garantía 19 (assistance) ──
    opts_19 = [
        GarantiaOption(id=22, garantia_id=19, nom_option='HANI', requires_montant=False),
        GarantiaOption(id=23, garantia_id=19, nom_option='IMTIAZ', requires_montant=False),
        GarantiaOption(id=24, garantia_id=19, nom_option='KAMEL', requires_montant=False),
        GarantiaOption(id=25, garantia_id=19, nom_option='KAMEL MAKMOUL', requires_montant=False),
    ]
    GarantiaOption.objects.bulk_create(opts_19)

    # ── Options for garantía 9 (dommages_collision) ──
    opts_9 = [
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
    ]
    GarantiaOption.objects.bulk_create(opts_9)

    # ── Franchises for option 1 (Valeur vénale) ──
    franchises_1 = [
        GarantiaFranchise(id=1, option_id=1, nom_franchise='Franchise 0% VIP'),
        GarantiaFranchise(id=2, option_id=1, nom_franchise='Franchise 3%'),
        GarantiaFranchise(id=3, option_id=1, nom_franchise='Franchise 5%'),
        GarantiaFranchise(id=4, option_id=1, nom_franchise='Franchise 10%'),
        GarantiaFranchise(id=5, option_id=1, nom_franchise='Franchise 15%'),
        GarantiaFranchise(id=6, option_id=1, nom_franchise='Franchise 20%'),
    ]
    GarantiaFranchise.objects.bulk_create(franchises_1)

    # ── Franchises for option 2 (Valeur à neuf) ──
    franchises_2 = [
        GarantiaFranchise(id=7, option_id=2, nom_franchise='Franchise 0% VIP'),
        GarantiaFranchise(id=8, option_id=2, nom_franchise='Franchise 3%'),
        GarantiaFranchise(id=9, option_id=2, nom_franchise='Franchise 5%'),
        GarantiaFranchise(id=10, option_id=2, nom_franchise='Franchise 10%'),
        GarantiaFranchise(id=11, option_id=2, nom_franchise='Franchise 15%'),
        GarantiaFranchise(id=12, option_id=2, nom_franchise='Franchise 20%'),
    ]
    GarantiaFranchise.objects.bulk_create(franchises_2)


def reverse_seed(apps, schema_editor):
    Garantia = apps.get_model('garantias', 'Garantia')
    GarantiaOption = apps.get_model('garantias', 'GarantiaOption')
    GarantiaFranchise = apps.get_model('garantias', 'GarantiaFranchise')
    GarantiaFranchise.objects.all().delete()
    GarantiaOption.objects.all().delete()
    Garantia.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('garantias', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(seed_data, reverse_seed),
    ]
