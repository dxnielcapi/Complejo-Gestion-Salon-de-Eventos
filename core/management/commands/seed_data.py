"""
Pobla la base de datos con los datos de ejemplo del PDF.
Uso: python manage.py seed_data
"""
from datetime import date, time
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from venues.models import (
    Espacio, EspacioCaracteristica, Paquete, PaqueteItem,
    ServicioAdicional, FechaOcupada,
)
from bookings.models import Reserva, ReservaServicio, ActividadReserva, PagoRegistro
from accounts.models import ClienteProfile
from operations.models import TareaPendiente


ESPACIOS = [
    {
        'nombre': 'Salón de Eventos Especializado',
        'slug': 'salon-de-eventos-especializado',
        'tipo': 'interior_climatizado',
        'descripcion': 'Nuestro salón principal con doble altura, pista de baile central, escenario y vista panorámica al jardín tropical. Ideal para bodas y celebraciones de gran formato.',
        'capacidad_max': 600,
        'precio_base': Decimal('185000'),
        'precio_max': Decimal('310000'),
        'color_card': '#C9A96E',
        'tags': 'salón principal · doble altura · pista de baile',
        'orden': 1,
        'caracteristicas': [
            'Pista de baile central de 120 m²',
            'Escenario profesional con iluminación',
            'Doble altura con techos de 8 m',
            'Vista panorámica al jardín tropical',
            'Sistema de sonido integrado',
            'Capacidad para hasta 600 invitados',
        ],
    },
    {
        'nombre': 'Jardín para Bodas',
        'slug': 'jardin-para-bodas',
        'tipo': 'exterior_tropical',
        'descripcion': 'Jardín ceremonial con palmeras, fuentes y pasillo nupcial enmarcado por buganvilias. Atardeceres caribeños inolvidables.',
        'capacidad_max': 350,
        'precio_base': Decimal('140000'),
        'precio_max': Decimal('245000'),
        'color_card': '#2D7A7A',
        'tags': 'jardín tropical · pasillo nupcial · gazebo',
        'orden': 2,
        'caracteristicas': [
            'Pasillo nupcial de 32 m',
            'Gazebo de madera tallada',
            'Iluminación ambiental al anochecer',
            'Zonas de cóctel bajo palapas',
            'Vista al mar parcial',
        ],
    },
    {
        'nombre': 'Terraza Panorámica',
        'slug': 'terraza-panoramica',
        'tipo': 'exterior_cubierto',
        'descripcion': 'Terraza elevada sobre el complejo con vista 270° al mar Caribe y la laguna. Cocteles al atardecer, cenas íntimas y celebraciones boutique.',
        'capacidad_max': 250,
        'precio_base': Decimal('120000'),
        'precio_max': Decimal('195000'),
        'color_card': '#E07E5D',
        'tags': 'terraza · vista al mar · atardecer',
        'orden': 3,
        'caracteristicas': [
            'Vista 270° al Mar Caribe',
            'Cubierta con estructura de madera',
            'Bar integrado con iluminación de ambiente',
            'Perfecta para cenas íntimas',
            'Acceso privado al complejo',
        ],
    },
    {
        'nombre': 'Salón de Celebraciones',
        'slug': 'salon-de-celebraciones',
        'tipo': 'interior_versatil',
        'descripcion': 'Espacio íntimo perfecto para bautizos, XV años y celebraciones familiares. Decoración personalizable y montajes flexibles.',
        'capacidad_max': 200,
        'precio_base': Decimal('85000'),
        'precio_max': Decimal('145000'),
        'color_card': '#2D7A7A',
        'tags': 'salón íntimo · iluminación cálida',
        'orden': 4,
        'caracteristicas': [
            'Iluminación cálida personalizable',
            'Sistema de sonido propio',
            'Montajes flexibles para diferentes eventos',
            'Cocina de apoyo contigua',
            'Estacionamiento exclusivo',
        ],
    },
]

PAQUETES = [
    {
        'nombre': 'basico',
        'descripcion_corta': 'Lo esencial para una celebración impecable.',
        'duracion_horas': 6,
        'precio_por_persona': Decimal('1850'),
        'es_mas_popular': False,
        'orden': 1,
        'items': [
            (True, 'Banquete de 3 tiempos · 2 opciones de menú'),
            (True, 'Música (DJ profesional)'),
            (True, 'Mobiliario base (mesas redondas, sillas tiffany)'),
            (True, 'Bebidas no alcohólicas ilimitadas'),
            (True, 'Coordinador de evento'),
            (False, 'Decoración temática'),
            (False, 'Bebidas alcohólicas'),
            (False, 'Artista en vivo'),
        ],
    },
    {
        'nombre': 'premium',
        'descripcion_corta': 'Una experiencia completa con decoración y barra abierta.',
        'duracion_horas': 6,
        'precio_por_persona': Decimal('2650'),
        'es_mas_popular': True,
        'orden': 2,
        'items': [
            (True, 'Banquete de 4 tiempos · 4 opciones de menú'),
            (True, 'Música (DJ profesional + coordinación)'),
            (True, 'Decoración floral y ambientación temática'),
            (True, 'Bebidas alcohólicas y mixología (barra premium)'),
            (True, 'Mobiliario premium + lounge'),
            (True, 'Coordinador y maestro de ceremonias'),
            (False, 'Artista o show en vivo'),
        ],
    },
    {
        'nombre': 'lujo',
        'descripcion_corta': 'Todo incluido, sin pendientes. Con artista en vivo.',
        'duracion_horas': 8,
        'precio_por_persona': Decimal('3950'),
        'es_mas_popular': False,
        'orden': 3,
        'items': [
            (True, 'Banquete gourmet de 5 tiempos · menú personalizado'),
            (True, 'DJ + artista en vivo (mariachi, trío, banda o show)'),
            (True, 'Decoración floral premium · diseño exclusivo'),
            (True, 'Barra abierta premium + mixología de autor'),
            (True, 'Mobiliario de lujo + lounges múltiples'),
            (True, 'Coordinador, MC y staff dedicado'),
            (True, 'Sesión fotográfica incluida (4 h)'),
        ],
    },
]

SERVICIOS = [
    ('Hora adicional de música', Decimal('4500'), 'fijo', 'music', 1),
    ('Decoración floral adicional', Decimal('18000'), 'fijo', 'sparkles', 2),
    ('Upgrade barra premium', Decimal('22000'), 'fijo', 'wine', 3),
    ('Tiempo extra de banquete', Decimal('320'), 'por_persona', 'clock', 4),
    ('Mariachi (1 hora)', Decimal('14500'), 'fijo', 'music', 5),
    ('Trío romántico (2 horas)', Decimal('9800'), 'fijo', 'music', 6),
    ('Banda en vivo (3 horas)', Decimal('38000'), 'fijo', 'music', 7),
    ('Pirotecnia fría', Decimal('16500'), 'fijo', 'sparkles', 8),
    ('Sesión fotográfica (4 h)', Decimal('12500'), 'fijo', 'camera', 9),
    ('Transporte para invitados', Decimal('18000'), 'fijo', 'bus', 10),
]

CLIENTES = [
    {'first_name': 'Sofía', 'last_name': 'Mendoza Carrillo', 'email': 'sofia.mendoza@correo.com', 'telefono': '+52 998 123 4567'},
    {'first_name': 'Andrés', 'last_name': 'López Rivera', 'email': 'andres.lopez@correo.com', 'telefono': '+52 998 234 5678'},
    {'first_name': 'Daniela', 'last_name': 'Cruz Beltrán', 'email': 'daniela.cruz@correo.com', 'telefono': '+52 998 345 6789'},
    {'first_name': 'Ricardo', 'last_name': 'Vega Ortega', 'email': 'ricardo.vega@correo.com', 'telefono': '+52 998 456 7890'},
    {'first_name': 'María Fernanda', 'last_name': 'Cano', 'email': 'mfcano@correo.com', 'telefono': '+52 998 567 8901'},
]


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de ejemplo del PDF'

    def handle(self, *args, **options):
        self.stdout.write('🌴 Creando datos de ejemplo...\n')
        self._crear_espacios()
        self._crear_paquetes()
        self._crear_servicios()
        self._crear_usuarios()
        self._crear_staff()
        self._crear_reservas()
        self._crear_tareas()
        self.stdout.write(self.style.SUCCESS('\n✅  Seed completado. Puedes hacer login con:\n'))
        self.stdout.write('   Staff:   admin@rivieramaya.mx / admin123\n')
        self.stdout.write('   Cliente: sofia.mendoza@correo.com / cliente123\n')

    def _crear_espacios(self):
        for d in ESPACIOS:
            caracteristicas = d.pop('caracteristicas')
            esp, created = Espacio.objects.update_or_create(
                slug=d['slug'], defaults=d
            )
            if created:
                for i, desc in enumerate(caracteristicas):
                    EspacioCaracteristica.objects.create(espacio=esp, descripcion=desc, orden=i)
                self.stdout.write(f'  Espacio: {esp.nombre}')

    def _crear_paquetes(self):
        for d in PAQUETES:
            items = d.pop('items')
            paq, created = Paquete.objects.update_or_create(
                nombre=d['nombre'], defaults=d
            )
            if created:
                for i, (incluido, desc) in enumerate(items):
                    PaqueteItem.objects.create(paquete=paq, descripcion=desc, incluido=incluido, orden=i)
                self.stdout.write(f'  Paquete: {paq.get_nombre_display()}')

    def _crear_servicios(self):
        for nombre, precio, tipo, icono, orden in SERVICIOS:
            s, created = ServicioAdicional.objects.update_or_create(
                nombre=nombre, defaults={'precio': precio, 'precio_tipo': tipo, 'icono_nombre': icono, 'orden': orden}
            )
            if created:
                self.stdout.write(f'  Servicio: {s.nombre}')

    def _crear_usuarios(self):
        for d in CLIENTES:
            user, created = User.objects.get_or_create(
                username=d['email'],
                defaults={'email': d['email'], 'first_name': d['first_name'], 'last_name': d['last_name']}
            )
            if created:
                user.set_password('cliente123')
                user.save()
                ClienteProfile.objects.get_or_create(user=user, defaults={'telefono': d['telefono']})
                self.stdout.write(f'  Cliente: {user.get_full_name()}')

    def _crear_staff(self):
        staff, created = User.objects.get_or_create(
            username='admin@rivieramaya.mx',
            defaults={
                'email': 'admin@rivieramaya.mx',
                'first_name': 'Lucía',
                'last_name': 'Aguirre',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            staff.set_password('admin123')
            staff.save()
            self.stdout.write('  Staff: Lucía Aguirre (admin)')

        coord, created = User.objects.get_or_create(
            username='lucia.aguirre@rivieramaya.mx',
            defaults={
                'email': 'lucia.aguirre@rivieramaya.mx',
                'first_name': 'Lucía',
                'last_name': 'Aguirre',
                'is_staff': True,
            }
        )
        if created:
            coord.set_password('admin123')
            coord.save()

    def _crear_reservas(self):
        coord = User.objects.filter(is_staff=True).first()
        datos_reservas = [
            {
                'codigo': 'RM-2026-0142',
                'email': 'sofia.mendoza@correo.com',
                'espacio_slug': 'jardin-para-bodas',
                'paquete_nombre': 'premium',
                'tipo_evento': 'boda',
                'fecha': date(2026, 6, 13),
                'hora_inicio': time(17, 0),
                'num_invitados': 280,
                'estado': 'confirmada',
                'total_evento': Decimal('882000'),
                'anticipo_pagado': Decimal('220500'),
                'notas_internas': 'Cliente solicita menú con opción vegetariana. Confirmar montaje tipo banquete redondo.',
                'servicios': ['Mariachi (1 hora)', 'Sesión fotográfica (4 h)'],
            },
            {
                'codigo': 'RM-2026-0148',
                'email': 'andres.lopez@correo.com',
                'espacio_slug': 'salon-de-eventos-especializado',
                'paquete_nombre': 'premium',
                'tipo_evento': 'xv_anos',
                'fecha': date(2026, 7, 4),
                'hora_inicio': time(18, 0),
                'num_invitados': 420,
                'estado': 'confirmada',
                'total_evento': Decimal('1989000'),
                'anticipo_pagado': Decimal('497250'),
                'notas_internas': '',
                'servicios': [],
            },
            {
                'codigo': 'RM-2026-0155',
                'email': 'daniela.cruz@correo.com',
                'espacio_slug': 'salon-de-celebraciones',
                'paquete_nombre': 'basico',
                'tipo_evento': 'bautizo',
                'fecha': date(2026, 5, 30),
                'hora_inicio': time(14, 0),
                'num_invitados': 120,
                'estado': 'pendiente_liquidacion',
                'total_evento': Decimal('222000'),
                'anticipo_pagado': Decimal('55500'),
                'notas_internas': '',
                'servicios': [],
            },
            {
                'codigo': 'RM-2026-0161',
                'email': 'ricardo.vega@correo.com',
                'espacio_slug': 'terraza-panoramica',
                'paquete_nombre': 'premium',
                'tipo_evento': 'aniversario',
                'fecha': date(2026, 6, 21),
                'hora_inicio': time(19, 0),
                'num_invitados': 180,
                'estado': 'confirmada',
                'total_evento': Decimal('499300'),
                'anticipo_pagado': Decimal('124825'),
                'notas_internas': '',
                'servicios': [],
            },
            {
                'codigo': 'RM-2026-0168',
                'email': 'mfcano@correo.com',
                'espacio_slug': 'terraza-panoramica',
                'paquete_nombre': 'lujo',
                'tipo_evento': 'boda',
                'fecha': date(2026, 8, 15),
                'hora_inicio': time(17, 0),
                'num_invitados': 220,
                'estado': 'confirmada',
                'total_evento': Decimal('898000'),
                'anticipo_pagado': Decimal('224500'),
                'notas_internas': '',
                'servicios': [],
            },
        ]

        for d in datos_reservas:
            if Reserva.objects.filter(codigo=d['codigo']).exists():
                continue
            try:
                cliente = User.objects.get(username=d['email'])
                espacio = Espacio.objects.get(slug=d['espacio_slug'])
                paquete = Paquete.objects.get(nombre=d['paquete_nombre'])
                servicios_nombres = d.pop('servicios')

                reserva = Reserva.objects.create(
                    codigo=d['codigo'],
                    cliente=cliente,
                    espacio=espacio,
                    paquete=paquete,
                    tipo_evento=d['tipo_evento'],
                    fecha=d['fecha'],
                    hora_inicio=d['hora_inicio'],
                    num_invitados=d['num_invitados'],
                    estado=d['estado'],
                    total_evento=d['total_evento'],
                    anticipo_pagado=d['anticipo_pagado'],
                    notas_internas=d['notas_internas'],
                    coordinador=coord,
                )

                for nombre in servicios_nombres:
                    try:
                        s = ServicioAdicional.objects.get(nombre=nombre)
                        ReservaServicio.objects.create(reserva=reserva, servicio=s)
                    except ServicioAdicional.DoesNotExist:
                        pass

                FechaOcupada.objects.get_or_create(espacio=espacio, fecha=d['fecha'], defaults={'motivo': 'reserva'})

                ActividadReserva.objects.create(
                    reserva=reserva,
                    descripcion='Reserva creada · Anticipo del 25% recibido',
                )
                self.stdout.write(f'  Reserva: {reserva.codigo}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Error en {d["codigo"]}: {e}'))

    def _crear_tareas(self):
        tareas = [
            ('Llamar a Daniela Cruz - confirmación menú', 'alta'),
            ('Revisar contrato proveedor pirotecnia', 'media'),
            ('Asignar coordinador a boda 15 ago', 'alta'),
        ]
        staff = User.objects.filter(is_staff=True).first()
        for desc, prioridad in tareas:
            TareaPendiente.objects.get_or_create(
                descripcion=desc,
                defaults={'prioridad': prioridad, 'asignado_a': staff}
            )
