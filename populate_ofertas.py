import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ofertas.models import TipoVehiculo, ModalidadSeguro, DuracionOferta, EstadoOferta, Oferta


def poblar_tipos_vehiculo():
    datos = [
        ('Moto', 1), ('Coche', 2), ('Camión', 3), ('Furgoneta', 4),
        ('Autobús', 5), ('Remolque', 6), ('Camioneta', 7), ('SUV', 8),
        ('Monovolumen', 9), ('Deportivo', 10), ('Furgoneta Camping', 11),
        ('Maquinaria Agrícola', 12), ('Maquinaria Industrial', 13),
    ]
    for nombre, orden in datos:
        TipoVehiculo.objects.update_or_create(nombre=nombre, defaults={'orden': orden, 'activo': True})
    print(f'  Tipos de vehículo: {len(datos)}')


def poblar_modalidades_seguro():
    datos = [
        ('Todo Riesgo', 'Cobertura completa del vehículo contra todo tipo de daños', 1),
        ('Terceros', 'Responsabilidad civil obligatoria', 2),
        ('Terceros Ampliado', 'Terceros + daños propios por causes limitados', 3),
        ('A Contra Riesgo', 'Solo robo e incendio', 4),
        ('Seguro de Vida', 'Cobertura en caso de fallecimiento o incapacidad', 5),
        ('Seguro de Vida Ahorro', 'Seguro de vida con componente de ahorro', 6),
        ('Seguro de Edificios', 'Daños materiales a edificios (incendio, inundación, etc.)', 7),
        ('Seguro de Hogar', 'Contenido del hogar, daños, responsabilidad civil', 8),
        ('Seguro de Salud', 'Asistencia médica, hospitalización, consultas', 9),
        ('Seguro de Comercio', 'Protección del local y actividad comercial', 10),
        ('Seguro de Responsabilidad Civil', 'Cubre daños a terceros por tu actividad', 11),
        ('Seguro de Transporte', 'Mercancías en tránsito terrestre, marítimo, aéreo', 12),
        ('Seguro Agrícola', 'Cultivos, ganería, maquinaria agrícola', 13),
        ('Seguro de Accidentes', 'Incapacidad temporal, permanente, muerte accidental', 14),
        ('Seguro de Deceso', 'Gastos funerarios y ayudas familiares', 15),
        ('Seguro de Equipajes', 'Pérdida, robo o daño de equipajes en viaje', 16),
        ('Seguro de Asistencia en Viaje', 'Asistencia médica en el extranjero, repatriación', 17),
        ('Seguro de Garantía Decenal', 'Daños estructurales en construcción (10 años)', 18),
        ('Seguro de Caución / Fianza', 'Garantía del cumplimiento de obligaciones', 19),
        ('Seguro de Ciberseguridad', 'Protección contra ciberataques y fraude digital', 20),
    ]
    for nombre, desc, orden in datos:
        ModalidadSeguro.objects.update_or_create(nombre=nombre, defaults={'descripcion': desc, 'orden': orden, 'activo': True})
    print(f'  Modalidades de seguro: {len(datos)}')


def poblar_duraciones():
    datos = [
        ('6 meses', 6, 1),
        ('1 año', 12, 2),
        ('2 años', 24, 3),
        ('3 años', 36, 4),
        ('5 años', 60, 5),
    ]
    for nombre, meses, orden in datos:
        DuracionOferta.objects.update_or_create(nombre=nombre, defaults={'meses': meses, 'orden': orden, 'activo': True})
    print(f'  Duraciones: {len(datos)}')


def poblar_estados():
    datos = [
        ('Borrador', 'secondary', 1),
        ('Enviada', 'primary', 2),
        ('En revisión', 'info', 3),
        ('Aceptada', 'success', 4),
        ('Rechazada', 'danger', 5),
        ('Caducada', 'warning', 6),
    ]
    for nombre, color, orden in datos:
        EstadoOferta.objects.update_or_create(nombre=nombre, defaults={'color': color, 'orden': orden, 'activo': True})
    print(f'  Estados: {len(datos)}')


def poblar_ofertas_ejemplo():
    if Oferta.objects.exists():
        print('  Ya existen ofertas, saltando ejemplo.')
        return

    tipo_moto = TipoVehiculo.objects.filter(nombre='Moto').first()
    tipo_coche = TipoVehiculo.objects.filter(nombre='Coche').first()
    tipo_suv = TipoVehiculo.objects.filter(nombre='SUV').first()
    tipo_furgoneta = TipoVehiculo.objects.filter(nombre='Furgoneta').first()

    mod_todo = ModalidadSeguro.objects.filter(nombre='Todo Riesgo').first()
    mod_terceros = ModalidadSeguro.objects.filter(nombre='Terceros').first()
    mod_vida = ModalidadSeguro.objects.filter(nombre='Seguro de Vida').first()
    mod_hogar = ModalidadSeguro.objects.filter(nombre='Seguro de Hogar').first()
    mod_edificio = ModalidadSeguro.objects.filter(nombre='Seguro de Edificios').first()
    mod_salud = ModalidadSeguro.objects.filter(nombre='Seguro de Salud').first()
    mod_rc = ModalidadSeguro.objects.filter(nombre='Seguro de Responsabilidad Civil').first()

    dur_6 = DuracionOferta.objects.filter(nombre='6 meses').first()
    dur_12 = DuracionOferta.objects.filter(nombre='1 año').first()

    est_borrador = EstadoOferta.objects.filter(nombre='Borrador').first()
    est_enviada = EstadoOferta.objects.filter(nombre='Enviada').first()
    est_aceptada = EstadoOferta.objects.filter(nombre='Aceptada').first()

    ofertas = [
        Oferta(
            cliente_nombre='Mohamed Benali', cliente_telefono='+33 6 12 34 56 78', cliente_email='m.benali@email.com',
            vehiculo_tipo=tipo_moto, vehiculo_marca='Yamaha', vehiculo_modelo='MT-07', vehiculo_matricula='AB-123-CD',
            vehiculo_potencia='70 cv', vehiculo_anio=2023,
            modalidad=mod_todo, duracion=dur_12, prima_estimada=420.00,
            estado=est_aceptada, notas='Cliente fiel, sin siniestros previos.',
        ),
        Oferta(
            cliente_nombre='Sophie Martin', cliente_telefono='+33 6 98 76 54 32', cliente_email='s.martin@email.com',
            vehiculo_tipo=tipo_coche, vehiculo_marca='Renault', vehiculo_modelo='Clio V', vehiculo_matricula='EF-456-GH',
            vehiculo_potencia='130 cv', vehiculo_anio=2024,
            modalidad=mod_todo, duracion=dur_12, prima_estimada=680.00,
            estado=est_enviada, notas='Primera vez que pide presupuesto.',
        ),
        Oferta(
            cliente_nombre='Ahmed El Fassi', cliente_telefono='+212 6 55 44 33 22', cliente_email='a.elfassi@email.com',
            vehiculo_tipo=tipo_suv, vehiculo_marca='Toyota', vehiculo_modelo='RAV4', vehiculo_matricula='IJ-789-KL',
            vehiculo_potencia='180 cv', vehiculo_anio=2022,
            modalidad=mod_terceros, duracion=dur_6, prima_estimada=290.00,
            estado=est_borrador, notas='Quiere comparar con otras aseguradoras.',
        ),
        Oferta(
            cliente_nombre='Fatima Zahra Amrani', cliente_telefono='+212 6 11 22 33 44', cliente_email='f.amrani@email.com',
            vehiculo_tipo=None, vehiculo_marca='', vehiculo_modelo='', vehiculo_matricula='',
            modalidad=mod_vida, duracion=dur_12, prima_estimada=360.00,
            estado=est_aceptada, notas='Seguro vida + ahorro. 3 hijos dependientes.',
        ),
        Oferta(
            cliente_nombre='Jean-Pierre Dubois', cliente_telefono='+33 6 77 88 99 00', cliente_email='jp.dubois@email.com',
            vehiculo_tipo=None, vehiculo_marca='', vehiculo_modelo='', vehiculo_matricula='',
            modalidad=mod_hogar, duracion=dur_12, prima_estimada=195.00,
            estado=est_enviada, notas='Piso 80m² en el centro. Robo + inundación + RC.',
        ),
        Oferta(
            cliente_nombre='Khadija Bennani', cliente_telefono='+212 6 00 11 22 33', cliente_email='k.bennani@email.com',
            vehiculo_tipo=None, vehiculo_marca='', vehiculo_modelo='', vehiculo_matricula='',
            modalidad=mod_edificio, duracion=dur_12, prima_estimada=1250.00,
            estado=est_borrador, notas='Local comercial 150m². Incendio + daños agua + terremoto.',
        ),
        Oferta(
            cliente_nombre='Carlos Mendez', cliente_telefono='+34 6 44 55 66 77', cliente_email='c.mendez@email.com',
            vehiculo_tipo=tipo_furgoneta, vehiculo_marca='Ford', vehiculo_modelo='Transit', vehiculo_matricula='MN-321-OP',
            vehiculo_potencia='170 cv', vehiculo_anio=2021,
            modalidad=mod_rc, duracion=dur_12, prima_estimada=520.00,
            estado=est_enviada, notas='Transporte de mercancías. RC profesional + daños propios.',
        ),
        Oferta(
            cliente_nombre='Amina Tazi', cliente_telefono='+212 6 88 77 66 55', cliente_email='a.tazi@email.com',
            vehiculo_tipo=None, vehiculo_marca='', vehiculo_modelo='', vehiculo_matricula='',
            modalidad=mod_salud, duracion=dur_12, prima_estimada=980.00,
            estado=est_borrador, notas='Cobertura familiar (2 adultos + 2 niños). Cuadro médico amplio.',
        ),
    ]
    Oferta.objects.bulk_create(ofertas)
    print(f'  Ofertas de ejemplo: {len(ofertas)}')


if __name__ == '__main__':
    print('Poblando tablas de ofertas...')
    poblar_tipos_vehiculo()
    poblar_modalidades_seguro()
    poblar_duraciones()
    poblar_estados()
    poblar_ofertas_ejemplo()
    print('¡Listo!')
