from django.db import migrations


def populate_ciudades(apps, schema_editor):
    CiudadSalat = apps.get_model('core', 'CiudadSalat')
    ciudades = [
        # Marruecos
        ('Rabat', 'Rabat', 'Morocco', 2, 'Marruecos', 1),
        ('Casablanca', 'Casablanca', 'Morocco', 2, 'Marruecos', 2),
        ('Marrakech', 'Marrakech', 'Morocco', 2, 'Marruecos', 3),
        ('Fès', 'Fes', 'Morocco', 2, 'Marruecos', 4),
        ('Tánger', 'Tangier', 'Morocco', 2, 'Marruecos', 5),
        # España
        ('Sevilla', 'Seville', 'Spain', 3, 'España', 10),
        ('Madrid', 'Madrid', 'Spain', 3, 'España', 11),
        ('Barcelona', 'Barcelona', 'Spain', 3, 'España', 12),
        ('Málaga', 'Malaga', 'Spain', 3, 'España', 13),
        ('Granada', 'Granada', 'Spain', 3, 'España', 14),
        # USA
        ('Nueva York', 'New York', 'United States', 2, 'USA', 20),
        ('Los Ángeles', 'Los Angeles', 'United States', 2, 'USA', 21),
        ('Chicago', 'Chicago', 'United States', 2, 'USA', 22),
        ('Houston', 'Houston', 'United States', 2, 'USA', 23),
        ('Miami', 'Miami', 'United States', 2, 'USA', 24),
        # Canadá
        ('Toronto', 'Toronto', 'Canada', 2, 'Canadá', 30),
        ('Montreal', 'Montreal', 'Canada', 2, 'Canadá', 31),
        ('Vancouver', 'Vancouver', 'Canada', 2, 'Canadá', 32),
        ('Calgary', 'Calgary', 'Canada', 2, 'Canadá', 33),
        # Sudáfrica
        ('Johannesburgo', 'Johannesburg', 'South Africa', 2, 'Sudáfrica', 40),
        ('Ciudad del Cabo', 'Cape Town', 'South Africa', 2, 'Sudáfrica', 41),
        ('Durban', 'Durban', 'South Africa', 2, 'Sudáfrica', 42),
        # Arabia Saudí
        ('La Meca', 'Makkah', 'Saudi Arabia', 4, 'Arabia Saudí', 50),
        ('Medina', 'Madinah', 'Saudi Arabia', 4, 'Arabia Saudí', 51),
        ('Yeda', 'Jeddah', 'Saudi Arabia', 4, 'Arabia Saudí', 52),
    ]
    for nombre, ciudad, pais, metodo, grupo, orden in ciudades:
        CiudadSalat.objects.get_or_create(
            nombre=nombre,
            defaults={
                'ciudad_api': ciudad,
                'pais_api': pais,
                'metodo': metodo,
                'grupo': grupo,
                'activa': True,
                'orden': orden,
            }
        )


def reverse_populate(apps, schema_editor):
    CiudadSalat = apps.get_model('core', 'CiudadSalat')
    CiudadSalat.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_ciudad_salat'),
    ]
    operations = [
        migrations.RunPython(populate_ciudades, reverse_populate),
    ]
