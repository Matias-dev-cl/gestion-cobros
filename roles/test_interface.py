from datetime import date
from pathlib import Path
from django.conf import settings
from django.test import TestCase, override_settings
from django.template.loader import get_template
from django.urls import reverse
from registro_cuentas.models import Cuenta
from usuarios.models import Usuario
from medidores.models import Medidor
from tarifas.models import Tarifa
from consumos.models import Consumo
from boletas.models import Boleta


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class InterfaceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = Cuenta.objects.create_user(username='admin', rol='admin')
        cls.user = Usuario.objects.create(nombre='Usuario Demo', rut='11.111.111-1',
            correo='demo@example.test', direccion='Dirección ficticia', telefono='+56900000000')
        cls.meter = Medidor.objects.create(codigo_serial='DEMO', usuario=cls.user)
        tariff = Tarifa.objects.create(valor=850)
        start = Consumo.objects.create(usuario=cls.user, medidor=cls.meter, tarifa_aplicada=tariff,
            fecha_consumo=date(2026, 1, 1), cantidad_consumida=100)
        cls.reading = Consumo.objects.create(usuario=cls.user, medidor=cls.meter, tarifa_aplicada=tariff,
            fecha_consumo=date(2026, 2, 1), cantidad_consumida=110)
        cls.bill = Boleta.objects.create(usuario=cls.user, consumo_inicio=start, consumo_fin=cls.reading)

    def test_all_html_templates_compile(self):
        for path in Path(settings.BASE_DIR).glob('*/templates/**/*.html'):
            name = path.relative_to(next(p for p in path.parents if p.name == 'templates')).as_posix()
            with self.subTest(template=name):
                get_template(name)

    def test_staff_lists_forms_details_and_confirmations_use_shared_shell(self):
        self.client.force_login(self.admin)
        routes = [(name, []) for name in [
            'roles:admin_dashboard', 'usuarios:lista_usuarios', 'usuarios:agregar_usuario',
            'medidores:historial_medidores', 'medidores:buscar_usuario_para_medidor',
            'consumos:lista_usuarios', 'consumos:lista_usuarios_consumos',
            'boletas:historial_recientes', 'boletas:seleccionar_usuario', 'boletas:buscar_usuario',
            'tarifas:historial_tarifas', 'registro_cuentas:lista_cuentas',
            'registro_cuentas:gestionar_cuenta', 'reportes:dashboard']]
        routes += [(name, [self.user.pk]) for name in [
            'usuarios:editar_usuario', 'usuarios:eliminar_usuario',
            'medidores:asignar_medidor_usuario', 'consumos:registrar_consumo',
            'consumos:historial_consumos', 'boletas:historial_usuario', 'boletas:seleccionar_consumos']]
        routes += [('medidores:confirmar_cambio_estado', [self.meter.pk]),
            ('boletas:imprimir_boleta', [self.bill.pk]),
            ('boletas:confirmar_eliminar_boleta', [self.bill.pk])]
        for name, args in routes:
            with self.subTest(route=name):
                response = self.client.get(reverse(name, args=args), follow=True)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'shared/base.html')
                self.assertContains(response, 'css/interface.css')

    def test_public_shell_is_consistent_even_with_staff_session(self):
        for logged_in in [False, True]:
            if logged_in:
                self.client.force_login(self.admin)
            for name in ['login:home', 'login:quienes_somos', 'reportes:revisar_consumo']:
                with self.subTest(route=name, logged_in=logged_in):
                    response = self.client.get(reverse(name))
                    self.assertContains(response, 'fw-public')
                    self.assertNotContains(response, '<aside class="sidebar">')
        self.client.logout()
        self.assertContains(self.client.get(reverse('login:login')), 'fw-public')

    def test_other_role_dashboards_share_the_shell(self):
        for role in ['operario', 'secretaria']:
            account = Cuenta.objects.create_user(username=role, rol=role)
            self.client.force_login(account)
            response = self.client.get(reverse(f'roles:{role}_dashboard'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'shared/base.html')
