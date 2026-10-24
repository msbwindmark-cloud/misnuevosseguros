from django.db import migrations


def populate_all_ciudades(apps, schema_editor):
    CiudadSalat = apps.get_model('core', 'CiudadSalat')
    ciudades = [
        # ── Marruecos ──────────────────────────────────────────
        ('Rabat', 'Rabat', 'Morocco', 2, 'Marruecos', 1),
        ('Casablanca', 'Casablanca', 'Morocco', 2, 'Marruecos', 2),
        ('Marrakech', 'Marrakech', 'Morocco', 2, 'Marruecos', 3),
        ('Fès', 'Fes', 'Morocco', 2, 'Marruecos', 4),
        ('Tánger', 'Tangier', 'Morocco', 2, 'Marruecos', 5),
        ('Agadir', 'Agadir', 'Morocco', 2, 'Marruecos', 6),
        ('Meknès', 'Meknes', 'Morocco', 2, 'Marruecos', 7),
        ('Oujda', 'Oujda', 'Morocco', 2, 'Marruecos', 8),
        ('Kenitra', 'Kenitra', 'Morocco', 2, 'Marruecos', 9),
        ('Tetuan', 'Tetouan', 'Morocco', 2, 'Marruecos', 240),
        ('Nador', 'Nador', 'Morocco', 2, 'Marruecos', 241),
        ('Al Hoceima', 'Al Hoceima', 'Morocco', 2, 'Marruecos', 242),
        ('El Aaiún', 'Laayoune', 'Morocco', 2, 'Marruecos', 243),
        ('Beni Mellal', 'Beni Mellal', 'Morocco', 2, 'Marruecos', 244),
        ('Taza', 'Taza', 'Morocco', 2, 'Marruecos', 245),
        ('Safi', 'Safi', 'Morocco', 2, 'Marruecos', 246),
        ('Mohammedia', 'Mohammedia', 'Morocco', 2, 'Marruecos', 247),
        ('Khouribga', 'Khouribga', 'Morocco', 2, 'Marruecos', 248),
        ('Errachidia', 'Errachidia', 'Morocco', 2, 'Marruecos', 249),
        ('Ifrane', 'Ifrane', 'Morocco', 2, 'Marruecos', 250),
        ('Bouznika', 'Bouznika', 'Morocco', 2, 'Marruecos', 251),

        # ── España ─────────────────────────────────────────────
        ('Sevilla', 'Seville', 'Spain', 3, 'España', 10),
        ('Madrid', 'Madrid', 'Spain', 3, 'España', 11),
        ('Barcelona', 'Barcelona', 'Spain', 3, 'España', 12),
        ('Málaga', 'Malaga', 'Spain', 3, 'España', 13),
        ('Granada', 'Granada', 'Spain', 3, 'España', 14),
        ('Valencia', 'Valencia', 'Spain', 3, 'España', 15),
        ('Bilbao', 'Bilbao', 'Spain', 3, 'España', 16),
        ('Zaragoza', 'Zaragoza', 'Spain', 3, 'España', 17),
        ('Alicante', 'Alicante', 'Spain', 3, 'España', 18),
        ('Córdoba', 'Cordoba', 'Spain', 3, 'España', 19),

        # ── USA ────────────────────────────────────────────────
        ('Nueva York', 'New York', 'United States', 2, 'USA', 20),
        ('Los Ángeles', 'Los Angeles', 'United States', 2, 'USA', 21),
        ('Chicago', 'Chicago', 'United States', 2, 'USA', 22),
        ('Houston', 'Houston', 'United States', 2, 'USA', 23),
        ('Miami', 'Miami', 'United States', 2, 'USA', 24),
        ('Phoenix', 'Phoenix', 'United States', 2, 'USA', 25),
        ('Filadelfia', 'Philadelphia', 'United States', 2, 'USA', 26),
        ('San Antonio', 'San Antonio', 'United States', 2, 'USA', 27),
        ('San Diego', 'San Diego', 'United States', 2, 'USA', 28),
        ('Dallas', 'Dallas', 'United States', 2, 'USA', 29),
        ('San José', 'San Jose', 'United States', 2, 'USA', 30),
        ('Austin', 'Austin', 'United States', 2, 'USA', 31),
        ('Jacksonville', 'Jacksonville', 'United States', 2, 'USA', 32),
        ('Fort Worth', 'Fort Worth', 'United States', 2, 'USA', 33),
        ('Columbus', 'Columbus', 'United States', 2, 'USA', 34),
        ('Charlotte', 'Charlotte', 'United States', 2, 'USA', 35),
        ('Indianápolis', 'Indianapolis', 'United States', 2, 'USA', 36),
        ('San Francisco', 'San Francisco', 'United States', 2, 'USA', 37),
        ('Seattle', 'Seattle', 'United States', 2, 'USA', 38),
        ('Denver', 'Denver', 'United States', 2, 'USA', 39),
        ('Washington DC', 'Washington', 'United States', 2, 'USA', 40),
        ('Nashville', 'Nashville', 'United States', 2, 'USA', 41),
        ('Oklahoma City', 'Oklahoma City', 'United States', 2, 'USA', 42),
        ('El Paso', 'El Paso', 'United States', 2, 'USA', 43),
        ('Boston', 'Boston', 'United States', 2, 'USA', 44),
        ('Portland', 'Portland', 'United States', 2, 'USA', 45),
        ('Las Vegas', 'Las Vegas', 'United States', 2, 'USA', 46),
        ('Memphis', 'Memphis', 'United States', 2, 'USA', 47),
        ('Louisville', 'Louisville', 'United States', 2, 'USA', 48),
        ('Baltimore', 'Baltimore', 'United States', 2, 'USA', 49),
        ('Milwaukee', 'Milwaukee', 'United States', 2, 'USA', 50),
        ('Albuquerque', 'Albuquerque', 'United States', 2, 'USA', 51),
        ('Tucson', 'Tucson', 'United States', 2, 'USA', 52),
        ('Fresno', 'Fresno', 'United States', 2, 'USA', 53),
        ('Sacramento', 'Sacramento', 'United States', 2, 'USA', 54),
        ('Mesa', 'Mesa', 'United States', 2, 'USA', 55),
        ('Kansas City', 'Kansas City', 'United States', 2, 'USA', 56),
        ('Atlanta', 'Atlanta', 'United States', 2, 'USA', 57),
        ('Omaha', 'Omaha', 'United States', 2, 'USA', 58),
        ('Colorado Springs', 'Colorado Springs', 'United States', 2, 'USA', 59),
        ('Raleigh', 'Raleigh', 'United States', 2, 'USA', 60),
        ('Long Beach', 'Long Beach', 'United States', 2, 'USA', 61),
        ('Virginia Beach', 'Virginia Beach', 'United States', 2, 'USA', 62),
        ('Oakland', 'Oakland', 'United States', 2, 'USA', 63),
        ('Minneapolis', 'Minneapolis', 'United States', 2, 'USA', 64),
        ('Tampa', 'Tampa', 'United States', 2, 'USA', 65),
        ('Orlando', 'Orlando', 'United States', 2, 'USA', 66),
        ('Detroit', 'Detroit', 'United States', 2, 'USA', 67),
        ('St. Louis', 'St. Louis', 'United States', 2, 'USA', 68),
        ('Pittsburgh', 'Pittsburgh', 'United States', 2, 'USA', 69),
        ('Cincinnati', 'Cincinnati', 'United States', 2, 'USA', 70),

        # ── Canadá ─────────────────────────────────────────────
        ('Toronto', 'Toronto', 'Canada', 2, 'Canadá', 80),
        ('Montreal', 'Montreal', 'Canada', 2, 'Canadá', 81),
        ('Vancouver', 'Vancouver', 'Canada', 2, 'Canadá', 82),
        ('Calgary', 'Calgary', 'Canada', 2, 'Canadá', 83),
        ('Ottawa', 'Ottawa', 'Canada', 2, 'Canadá', 84),
        ('Edmonton', 'Edmonton', 'Canada', 2, 'Canadá', 85),
        ('Quebec', 'Quebec', 'Canada', 2, 'Canadá', 86),
        ('Winnipeg', 'Winnipeg', 'Canada', 2, 'Canadá', 87),
        ('Hamilton', 'Hamilton', 'Canada', 2, 'Canadá', 88),
        ('Kitchener', 'Kitchener', 'Canada', 2, 'Canadá', 89),
        ('Halifax', 'Halifax', 'Canada', 2, 'Canadá', 90),
        ('Victoria', 'Victoria', 'Canada', 2, 'Canadá', 91),
        ('Saskatoon', 'Saskatoon', 'Canada', 2, 'Canadá', 92),
        ('Regina', 'Regina', 'Canada', 2, 'Canadá', 93),
        ("St. John's", "St. John's", 'Canada', 2, 'Canadá', 94),
        ('Kelowna', 'Kelowna', 'Canada', 2, 'Canadá', 95),
        ('Barrie', 'Barrie', 'Canada', 2, 'Canadá', 96),
        ('Sudbury', 'Sudbury', 'Canada', 2, 'Canadá', 97),
        ('Kingston', 'Kingston', 'Canada', 2, 'Canadá', 98),
        ('London ON', 'London', 'Canada', 2, 'Canadá', 99),
        ('Windsor', 'Windsor', 'Canada', 2, 'Canadá', 100),

        # ── Sudáfrica ──────────────────────────────────────────
        ('Johannesburgo', 'Johannesburg', 'South Africa', 2, 'Sudáfrica', 110),
        ('Ciudad del Cabo', 'Cape Town', 'South Africa', 2, 'Sudáfrica', 111),
        ('Durban', 'Durban', 'South Africa', 2, 'Sudáfrica', 112),
        ('Pretoria', 'Pretoria', 'South Africa', 2, 'Sudáfrica', 113),
        ('Port Elizabeth', 'Port Elizabeth', 'South Africa', 2, 'Sudáfrica', 114),
        ('Bloemfontein', 'Bloemfontein', 'South Africa', 2, 'Sudáfrica', 115),
        ('East London', 'East London', 'South Africa', 2, 'Sudáfrica', 116),
        ('Kimberley', 'Kimberley', 'South Africa', 2, 'Sudáfrica', 117),
        ('Nelspruit', 'Nelspruit', 'South Africa', 2, 'Sudáfrica', 118),
        ('Polokwane', 'Polokwane', 'South Africa', 2, 'Sudáfrica', 119),
        ('Soweto', 'Soweto', 'South Africa', 2, 'Sudáfrica', 120),

        # ── Arabia Saudí ───────────────────────────────────────
        ('La Meca', 'Makkah', 'Saudi Arabia', 4, 'Arabia Saudí', 130),
        ('Medina', 'Madinah', 'Saudi Arabia', 4, 'Arabia Saudí', 131),
        ('Yeda', 'Jeddah', 'Saudi Arabia', 4, 'Arabia Saudí', 132),
        ('Riad', 'Riyadh', 'Saudi Arabia', 4, 'Arabia Saudí', 133),
        ('Dammam', 'Dammam', 'Saudi Arabia', 4, 'Arabia Saudí', 134),
        ('Al Khobar', 'Khobar', 'Saudi Arabia', 4, 'Arabia Saudí', 135),
        ('Tabuk', 'Tabuk', 'Saudi Arabia', 4, 'Arabia Saudí', 136),
        ('Buraidah', 'Buraidah', 'Saudi Arabia', 4, 'Arabia Saudí', 137),
        ('Abha', 'Abha', 'Saudi Arabia', 4, 'Arabia Saudí', 138),
        ('Taif', 'Taif', 'Saudi Arabia', 4, 'Arabia Saudí', 139),
        ('Khamis Mushait', 'Khamis Mushait', 'Saudi Arabia', 4, 'Arabia Saudí', 140),
        ("Ha'il", 'Hail', 'Saudi Arabia', 4, 'Arabia Saudí', 141),
        ('Jubail', 'Jubail', 'Saudi Arabia', 4, 'Arabia Saudí', 142),
        ('Yanbu', 'Yanbu', 'Saudi Arabia', 4, 'Arabia Saudí', 143),

        # ── UK ─────────────────────────────────────────────────
        ('Londres', 'London', 'United Kingdom', 3, 'UK', 150),
        ('Birmingham', 'Birmingham', 'United Kingdom', 3, 'UK', 151),
        ('Mánchester', 'Manchester', 'United Kingdom', 3, 'UK', 152),
        ('Leeds', 'Leeds', 'United Kingdom', 3, 'UK', 153),
        ('Glasgow', 'Glasgow', 'United Kingdom', 3, 'UK', 154),
        ('Edimburgo', 'Edinburgh', 'United Kingdom', 3, 'UK', 155),
        ('Liverpool', 'Liverpool', 'United Kingdom', 3, 'UK', 156),
        ('Bradford', 'Bradford', 'United Kingdom', 3, 'UK', 157),
        ('Bristol', 'Bristol', 'United Kingdom', 3, 'UK', 158),
        ('Sheffield', 'Sheffield', 'United Kingdom', 3, 'UK', 159),

        # ── Francia ────────────────────────────────────────────
        ('París', 'Paris', 'France', 12, 'Francia', 160),
        ('Lyon', 'Lyon', 'France', 12, 'Francia', 161),
        ('Marsella', 'Marseille', 'France', 12, 'Francia', 162),
        ('Toulouse', 'Toulouse', 'France', 12, 'Francia', 163),
        ('Estrasburgo', 'Strasbourg', 'France', 12, 'Francia', 164),
        ('Niza', 'Nice', 'France', 12, 'Francia', 165),
        ('Burdeos', 'Bordeaux', 'France', 12, 'Francia', 166),
        ('Lille', 'Lille', 'France', 12, 'Francia', 167),
        ('Rennes', 'Rennes', 'France', 12, 'Francia', 168),
        ('Montpellier', 'Montpellier', 'France', 12, 'Francia', 169),

        # ── Alemania ───────────────────────────────────────────
        ('Berlín', 'Berlin', 'Germany', 3, 'Alemania', 170),
        ('Múnich', 'Munich', 'Germany', 3, 'Alemania', 171),
        ('Frankfurt', 'Frankfurt', 'Germany', 3, 'Alemania', 172),
        ('Hamburgo', 'Hamburg', 'Germany', 3, 'Alemania', 173),
        ('Colonia', 'Cologne', 'Germany', 3, 'Alemania', 174),
        ('Stuttgart', 'Stuttgart', 'Germany', 3, 'Alemania', 175),
        ('Düsseldorf', 'Dusseldorf', 'Germany', 3, 'Alemania', 176),
        ('Dresde', 'Dresden', 'Germany', 3, 'Alemania', 177),
        ('Hannover', 'Hannover', 'Germany', 3, 'Alemania', 178),
        ('Núremberg', 'Nuremberg', 'Germany', 3, 'Alemania', 179),

        # ── Turquía ────────────────────────────────────────────
        ('Estambul', 'Istanbul', 'Turkey', 13, 'Turquía', 180),
        ('Ankara', 'Ankara', 'Turkey', 13, 'Turquía', 181),
        ('Izmir', 'Izmir', 'Turkey', 13, 'Turquía', 182),
        ('Bursa', 'Bursa', 'Turkey', 13, 'Turquía', 183),
        ('Antalya', 'Antalya', 'Turkey', 13, 'Turquía', 184),
        ('Adana', 'Adana', 'Turkey', 13, 'Turquía', 185),
        ('Konya', 'Konya', 'Turkey', 13, 'Turquía', 186),
        ('Gaziantep', 'Gaziantep', 'Turkey', 13, 'Turquía', 187),

        # ── Egipto ─────────────────────────────────────────────
        ('El Cairo', 'Cairo', 'Egypt', 5, 'Egipto', 190),
        ('Alejandría', 'Alexandria', 'Egypt', 5, 'Egipto', 191),
        ('Giza', 'Giza', 'Egypt', 5, 'Egipto', 192),
        ('Luxor', 'Luxor', 'Egypt', 5, 'Egipto', 193),
        ('Asuán', 'Aswan', 'Egypt', 5, 'Egipto', 194),

        # ── Golfo ──────────────────────────────────────────────
        ('Dubái', 'Dubai', 'United Arab Emirates', 8, 'Golfo', 200),
        ('Abu Dabi', 'Abu Dhabi', 'United Arab Emirates', 8, 'Golfo', 201),
        ('Sharjah', 'Sharjah', 'United Arab Emirates', 8, 'Golfo', 202),
        ('Doha', 'Doha', 'Qatar', 10, 'Golfo', 203),
        ('Kuwait City', 'Kuwait City', 'Kuwait', 8, 'Golfo', 204),
        ('Manama', 'Manama', 'Bahrain', 8, 'Golfo', 205),
        ('Mascat', 'Muscat', 'Oman', 8, 'Golfo', 206),

        # ── Pakistán ───────────────────────────────────────────
        ('Karachi', 'Karachi', 'Pakistan', 1, 'Pakistán', 210),
        ('Lahore', 'Lahore', 'Pakistan', 1, 'Pakistán', 211),
        ('Islamabad', 'Islamabad', 'Pakistan', 1, 'Pakistán', 212),
        ('Faisalabad', 'Faisalabad', 'Pakistan', 1, 'Pakistán', 213),
        ('Rawalpindi', 'Rawalpindi', 'Pakistan', 1, 'Pakistán', 214),
        ('Multan', 'Multan', 'Pakistan', 1, 'Pakistán', 215),
        ('Peshawar', 'Peshawar', 'Pakistan', 1, 'Pakistán', 216),
        ('Quetta', 'Quetta', 'Pakistan', 1, 'Pakistán', 217),

        # ── India ──────────────────────────────────────────────
        ('Bombay', 'Mumbai', 'India', 1, 'India', 220),
        ('Delhi', 'Delhi', 'India', 1, 'India', 221),
        ('Hyderabad', 'Hyderabad', 'India', 1, 'India', 222),
        ('Bangalore', 'Bangalore', 'India', 1, 'India', 223),
        ('Chennai', 'Chennai', 'India', 1, 'India', 224),
        ('Calcuta', 'Kolkata', 'India', 1, 'India', 225),
        ('Ahmedabad', 'Ahmedabad', 'India', 1, 'India', 226),
        ('Pune', 'Pune', 'India', 1, 'India', 227),

        # ── Indonesia ──────────────────────────────────────────
        ('Yakarta', 'Jakarta', 'Indonesia', 11, 'Indonesia', 230),
        ('Surabaya', 'Surabaya', 'Indonesia', 11, 'Indonesia', 231),
        ('Bandung', 'Bandung', 'Indonesia', 11, 'Indonesia', 232),
        ('Semarang', 'Semarang', 'Indonesia', 11, 'Indonesia', 233),
        ('Medan', 'Medan', 'Indonesia', 11, 'Indonesia', 234),
        ('Makassar', 'Makassar', 'Indonesia', 11, 'Indonesia', 235),

        # ── Senegal ────────────────────────────────────────────
        ('Dakar', 'Dakar', 'Senegal', 2, 'Senegal', 260),
        ('Thiès', 'Thies', 'Senegal', 2, 'Senegal', 261),
        ('Saint-Louis', 'Saint-Louis', 'Senegal', 2, 'Senegal', 262),

        # ── Costa de Marfil ────────────────────────────────────
        ('Abiyán', 'Abidjan', "Cote d'Ivoire", 2, 'Costa de Marfil', 270),

        # ── Malí ───────────────────────────────────────────────
        ('Bamako', 'Bamako', 'Mali', 2, 'Malí', 280),

        # ── Argelia ────────────────────────────────────────────
        ('Argel', 'Algiers', 'Algeria', 5, 'Argelia', 290),
        ('Orán', 'Oran', 'Algeria', 5, 'Argelia', 291),
        ('Constantina', 'Constantine', 'Algeria', 5, 'Argelia', 292),
        ('Annaba', 'Annaba', 'Algeria', 5, 'Argelia', 293),

        # ── Túnez ──────────────────────────────────────────────
        ('Túnez', 'Tunis', 'Tunisia', 5, 'Túnez', 300),
        ('Sfax', 'Sfax', 'Tunisia', 5, 'Túnez', 301),
        ('Sousse', 'Sousse', 'Tunisia', 5, 'Túnez', 302),

        # ── Jordania ───────────────────────────────────────────
        ('Amán', 'Amman', 'Jordan', 8, 'Jordania', 310),
        ('Irbid', 'Irbid', 'Jordan', 8, 'Jordania', 311),

        # ── Líbano ─────────────────────────────────────────────
        ('Beirut', 'Beirut', 'Lebanon', 8, 'Líbano', 320),

        # ── Iraq ───────────────────────────────────────────────
        ('Bagdad', 'Baghdad', 'Iraq', 8, 'Iraq', 330),
        ('Basora', 'Basra', 'Iraq', 8, 'Iraq', 331),
        ('Erbil', 'Erbil', 'Iraq', 8, 'Iraq', 332),

        # ── Bangladesh ─────────────────────────────────────────
        ('Daca', 'Dhaka', 'Bangladesh', 2, 'Bangladesh', 340),
        ('Chittagong', 'Chittagong', 'Bangladesh', 2, 'Bangladesh', 341),

        # ── Malasia ────────────────────────────────────────────
        ('Kuala Lumpur', 'Kuala Lumpur', 'Malaysia', 1, 'Malasia', 350),
        ('Penang', 'Penang', 'Malasia', 1, 'Malasia', 351),
        ('Johor Bahru', 'Johor Bahru', 'Malasia', 1, 'Malasia', 352),

        # ── Singapur ───────────────────────────────────────────
        ('Singapur', 'Singapore', 'Singapore', 11, 'Singapur', 360),

        # ── Rusia ──────────────────────────────────────────────
        ('Moscú', 'Moscow', 'Russia', 14, 'Rusia', 370),
        ('San Petersburgo', 'Saint Petersburg', 'Russia', 14, 'Rusia', 371),

        # ── China ──────────────────────────────────────────────
        ('Pekín', 'Beijing', 'China', 1, 'China', 380),
        ('Shanghái', 'Shanghai', 'China', 1, 'China', 381),

        # ── Japón ──────────────────────────────────────────────
        ('Tokio', 'Tokyo', 'Japan', 1, 'Japón', 390),
        ('Osaka', 'Osaka', 'Japan', 1, 'Japón', 391),
    ]
    for nombre, ciudad, pais, metodo, grupo, orden in ciudades:
        CiudadSalat.objects.update_or_create(
            ciudad_api=ciudad, pais_api=pais,
            defaults={
                'nombre': nombre, 'metodo': metodo,
                'grupo': grupo, 'activa': True, 'orden': orden,
            }
        )


def reverse_populate(apps, schema_editor):
    CiudadSalat = apps.get_model('core', 'CiudadSalat')
    CiudadSalat.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_populate_ciudades'),
    ]
    operations = [
        migrations.RunPython(populate_all_ciudades, reverse_populate),
    ]
