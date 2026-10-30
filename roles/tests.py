from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from boletas.models import Boleta
from registro_cuentas.models import Cuenta
from usuarios.models import Usuario
from .dashboard import dashboard_context


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class DashboardTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create(nombre='Usuario Demo', rut='11.111.111-1',
            correo='demo@example.test', direccion='Dirección ficticia', telefono='+56900000000')

    def bill(self, day, amount, volume, paid=False):
        return Boleta.objects.create(usuario=self.user, fecha_emision=day,
            consumo_total=volume, total_a_pagar=amount, tarifa_base=100, pagado=paid)

    def test_month_totals_exclude_other_years_and_future(self):
        self.bill(date(2026, 1, 2), 1000, 10, True)
        self.bill(date(2026, 1, 3), 500, 5)
        self.bill(date(2025, 1, 3), 9000, 90)
        self.bill(date(2026, 2, 3), 8000, 80)
        data = dashboard_context(date(2026, 1, 15))
        self.assertEqual(data['facturado_mes'], Decimal('1500'))
        self.assertEqual(data['pagado_mes'], Decimal('1000'))
        self.assertEqual(data['pendiente_mes'], Decimal('500'))
        self.assertEqual(data['volumen_facturado_mes'], Decimal('15'))
        self.assertEqual(data['trend'][-1]['total'], Decimal('15'))
        self.assertEqual(data['trend'][0]['label'], 'Ago 2025')

    def test_empty_dashboard_has_zeroes_and_six_months(self):
        data = dashboard_context(date(2026, 1, 15))
        self.assertEqual(data['porcentaje_pagado'], 0)
        self.assertEqual(len(data['trend']), 6)
        self.assertTrue(all(point['total'] == 0 for point in data['trend']))

    def test_admin_page_and_role_restriction(self):
        self.assertRedirects(self.client.get('/roles/admin-dashboard/'),
            '/iniciar-sesion/?next=/roles/admin-dashboard/', fetch_redirect_response=False)
        account = Cuenta.objects.create_user(username='operario', rol='operario')
        self.client.force_login(account)
        self.assertEqual(self.client.get('/roles/admin-dashboard/').status_code, 403)
        account.rol = 'admin'
        account.save()
        response = self.client.get('/roles/admin-dashboard/')
        self.assertContains(response, 'Todavía no hay boletas')


class BillingValidationTests(TestCase):
    def bill(self, **overrides):
        start = SimpleNamespace(usuario_id=1, medidor_id=1, cantidad_consumida=Decimal('100'), fecha_consumo=date(2026, 1, 1))
        end = SimpleNamespace(usuario_id=1, medidor_id=1, cantidad_consumida=Decimal('110'), fecha_consumo=date(2026, 2, 1))
        for key, value in overrides.items():
            setattr(end, key, value)
        bill = Boleta(usuario_id=1)
        # Model descriptors require real Consumo objects; use unsaved model instances.
        from consumos.models import Consumo
        bill.consumo_inicio = Consumo(pk=1, **vars(start))
        bill.consumo_fin = Consumo(pk=2, **vars(end))
        return bill

    def test_rejects_another_user_or_meter_and_decreasing_reading(self):
        for change in [{'usuario_id': 2}, {'medidor_id': 2}, {'cantidad_consumida': Decimal('90')}]:
            with self.subTest(change=change), self.assertRaises(ValidationError):
                self.bill(**change).clean()

    def test_accepts_ordered_readings_from_same_meter(self):
        self.bill().clean()
