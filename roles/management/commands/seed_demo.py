"""Carga idempotente de datos ficticios para explorar el portafolio."""
from datetime import date
from decimal import Decimal
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from usuarios.models import Usuario
from medidores.models import Medidor
from tarifas.models import Tarifa
from boletas.models import Boleta


class Command(BaseCommand):
    help = 'Carga datos ficticios de portafolio. Solo disponible con DEBUG=True.'

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Este comando es exclusivo del entorno de desarrollo.')
        tariff = Tarifa.objects.filter(activo=True).first()
        if tariff is None:
            Tarifa.objects.create(valor=850, descripcion='Tarifa de demostración')
        today = timezone.localdate()
        names = ['Camila Torres', 'Diego Rojas', 'Valentina Soto', 'Tomás Fuentes', 'Antonia Pérez', 'Lucas Morales']
        for n, name in enumerate(names):
            user, _ = Usuario.objects.get_or_create(correo=f'usuario{n+1}@example.test', defaults={
                'nombre': name, 'rut': f'99.000.00{n}-K', 'direccion': f'Calle de demostración {n+1}',
                'telefono': '+56900000000'})
            Medidor.objects.get_or_create(codigo_serial=f'DEMO-{n+1:03d}', defaults={
                'usuario': user, 'estado': 'mantenimiento' if n == 5 else 'activo'})
            for offset in range(6):
                index = today.year * 12 + today.month - 1 - offset
                issued = date(index // 12, index % 12 + 1, min(n+3, today.day) if offset == 0 else n+3)
                volume = Decimal(9+n*2+(5-offset))
                # Fixtures de facturación independientes del hardware y de lecturas reales.
                Boleta.objects.get_or_create(usuario=user, fecha_emision=issued,
                    consumo_inicio=None, consumo_fin=None, defaults={
                    'consumo_total': volume, 'tarifa_base': 850, 'total_a_pagar': volume*850,
                    'pagado': n < 4 or offset > 1})
        self.stdout.write(self.style.SUCCESS('Datos ficticios preparados: 6 usuarios y 36 boletas. No se crearon credenciales.'))
