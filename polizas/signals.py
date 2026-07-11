from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Poliza, PolizaCopia


@receiver(post_save, sender=Poliza)
def crear_copia_poliza(sender, instance, created, **kwargs):
    if created:
        PolizaCopia.objects.create(
            poliza_original=instance,
            fecha_hoy=instance.fecha_hoy,
            letype=instance.letype,
            attestation=instance.attestation,
            police=instance.police,
            marque=instance.marque,
            matricule=instance.matricule,
            produit=instance.produit,
            designation=instance.designation,
            assure=instance.assure,
            du=instance.du,
            au=instance.au,
            totale=instance.totale,
            espece=instance.espece,
            cheque=instance.cheque,
            virement=instance.virement,
            reste=instance.reste,
        )
