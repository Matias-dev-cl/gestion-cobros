# Arquitectura y alcance

FlowWeb es un monolito Django con páginas renderizadas en servidor. La interfaz administrativa nueva usa CSS local y no requiere un proceso de compilación ni servicios de gráficos externos. Los módulos heredados conservan sus interfaces originales.

## Flujo funcional

Usuario del servicio → medidor → lecturas acumuladas → diferencia entre lecturas → boleta → estado de pago → indicadores.

Las cuentas de acceso son distintas de los usuarios del servicio. `Cuenta` extiende el usuario de Django y define los roles admin, secretaria y operario. Las vistas protegidas comprueban el rol en el servidor.

## Indicadores del panel

`roles/dashboard.py` construye el contexto del administrador:

- Facturado: suma del monto de boletas emitidas durante el mes calendario actual.
- Pagado: monto de esas mismas boletas cuyo estado actual es pagado. No representa un flujo de caja por fecha de pago.
- Pendiente: diferencia entre ambos montos para ese mes; no es la deuda histórica total.
- Volumen facturado: suma de las diferencias de lectura guardadas en esas boletas. No es el volumen físico distribuido ni una suma de lecturas acumuladas.
- Tendencia: seis meses consecutivos agrupados por mes y año de emisión, completando meses sin datos con cero.

Las boletas validan que las lecturas correspondan al usuario, al mismo medidor, a fechas ordenadas y a un contador no decreciente. No se alteró la fórmula heredada de tarifas: requiere definir reglas comerciales antes de usarla en un comité real.

## Demostración local

Con DEBUG=True, ejecutar `python manage.py seed_demo`. Crea registros ficticios identificables con correos `example.test` y seriales `DEMO-`. Se puede repetir sin duplicar el conjunto. No crea una contraseña pública ni requiere Supabase. Las boletas de muestra contienen totales preparados sin lecturas asociadas y no permiten validar el flujo completo de medición.

## Validación

`python manage.py test` cubre acceso al panel por rol, datos vacíos, separación de años y meses, conciliación de totales y validaciones de lecturas, además de las pruebas de login existentes. La integración ESP32 y Supabase requiere verificación externa.

## Próximas etapas

1. Extender el sistema visual a usuarios, lecturas y boletas, con formularios accesibles y errores contextualizados.
2. Definir tarifas por tramos y periodos, impedir facturación duplicada y agregar pruebas de los límites de cálculo.
3. Reemplazar la simulación pública de pagos por un flujo claramente demostrativo, sin pedir datos de tarjeta, antes de desplegar una demo pública.
4. Revisar privacidad de la consulta pública, permisos de cada operación y actualizaciones de dependencias antes del despliegue.
5. Completar capturas, demostración reproducible y pruebas de extremo a extremo.

La aplicación es un portafolio en evolución, no una solución certificada para facturación ni lista para producción.
