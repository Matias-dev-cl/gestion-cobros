# Gestión de consumos y cobros de agua

Aplicación web para administrar usuarios, medidores, lecturas de consumo, tarifas y cobros de agua. Proyecto de portafolio con Python y Django, interfaces renderizadas en servidor e integración experimental con medidores ESP32.

## Funciones incluidas

- Gestión de usuarios, cuentas y roles de administrador, secretaría y operario.
- Asignación y administración de medidores.
- Registro de lecturas con validaciones y cálculo de cobros por tarifas.
- Generación y descarga de boletas en PDF.
- Paneles y reportes de pagos, deuda y consumo.
- Código ESP32 y sincronización de lecturas desde una tabla externa en Supabase.

## Tecnologías

Python, Django, ORM de Django, PostgreSQL/Supabase, HTML, JavaScript, Tailwind CSS, Bootstrap y Chart.js. La generación de PDF utiliza xhtml2pdf. El frontend usa plantillas de Django, no React. El firmware utiliza ESP32, un sensor de flujo YF-S201 y un reloj DS3231.

## Inicio local en Windows PowerShell

Recomendado: Python 3.11 y un entorno virtual. No se necesita Node para explorar las interfaces que usan los estilos CDN.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DJANGO_SECRET_KEY = (python -c "import secrets; print(secrets.token_urlsafe(50))")
$env:DJANGO_DEBUG = "True"
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abrir http://127.0.0.1:8000/. La cuenta creada necesita un rol apropiado para acceder a cada panel; el modelo de cuentas define administrador, secretaría y operario. No se incluyen cuentas ni contraseñas compartidas.

SQLite es el valor predeterminado para exploración local. Para utilizar PostgreSQL, exportar las variables DB_HOST, DB_NAME, DB_USER, DB_PASSWORD y DB_PORT descritas en `.env.example`. Ese archivo es una referencia y no se carga automáticamente.

## Panel de portafolio

El panel administrativo incluye indicadores de facturación, tendencia de seis meses, estado del servicio y boletas recientes. Para explorarlo con información ficticia: `python manage.py seed_demo` con DEBUG=True. El comando se puede repetir sin duplicar los registros de muestra.

Consultar [arquitectura y decisiones](docs/architecture.md) para las definiciones de indicadores, límites del proyecto y próximas mejoras. Ejecutar `python manage.py test` para verificar los cálculos, validaciones y permisos cubiertos.

## Integración IoT

`Codigo_Esp32.txt` contiene el prototipo del medidor. Sus valores de conexión están reemplazados por marcadores. La sincronización requiere PostgreSQL/Supabase y la tabla externa `medidas`, mapeada por `MedidaRaw`; las migraciones no crean esa tabla. El funcionamiento del hardware y de servicios externos debe validarse en el entorno correspondiente.

## Alcance y estado

Proyecto demostrativo, no un servicio de facturación certificado ni una integración de pagos reales. El módulo de reportes incluye simulación de pagos. No se garantiza que esté listo para producción. Las dependencias y recursos CDN requieren revisión antes de un despliegue real. El proceso de Tailwind heredado debe revisarse si se desea compilar estilos localmente.

## Procedencia

Esta copia de portafolio parte de https://github.com/MattyC4/gestion_cobros y conserva la estructura funcional del proyecto. La preparación para publicación incluye configuración por variables de entorno, eliminación de archivos generados y documentación de ejecución. No se atribuye autoría individual de todos los módulos.
