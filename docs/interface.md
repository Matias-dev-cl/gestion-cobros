# Interfaz compartida de FlowWeb

## Estructura

Las nueve bases de módulos extienden `roles/templates/shared/base.html`. Esto evita que la navegación o los recursos visuales cambien entre usuarios, medidores, consumos, tarifas, cuentas, boletas, reportes y paneles por rol. El panel del administrador también extiende esa base.

El procesador `roles.context_processors.interface` distingue las páginas públicas (portal, acceso, comité y consultas) de las páginas de gestión. La sesión de un funcionario no transforma la portada pública en un panel interno. Las vistas mantienen sus validaciones de permisos; ocultar enlaces no sustituye esa validación.

## Identidad visual

- Color principal verde agua `#187d78`; texto `#243b47`, fondo `#f5f7f9` y superficies blancas.
- Tipografía Segoe UI o equivalente del sistema, títulos con peso moderado y jerarquía estable.
- Botones, campos, tarjetas y confirmaciones comparten bordes, foco y radios.
- Estados semánticos verdes, ámbar y rojos; los gráficos usan la misma paleta.
- La sección activa se indica con `aria-current`. Los controles de contraseña tienen etiqueta accesible y estado.
- Los mensajes generales se muestran una sola vez en la base común; los errores de campos permanecen junto a sus formularios.

## Pantallas pequeñas

La navegación lateral pasa a una franja horizontal desplazable. Las tarjetas se reorganizan, los formularios ocupan el ancho disponible y las tablas se desplazan en su propio contenedor. Se revisaron las vistas principales a 390 px, incluidos acceso y consulta pública.

## Comprobaciones

`roles/test_interface.py` compila las plantillas y comprueba la carga de 24 rutas administrativas (listas, formularios, detalles y confirmaciones), páginas públicas con y sin sesión, y paneles de operario y secretaría. También se revisaron visualmente portada, acceso, formulario de usuarios, cuentas, medidores, consumos, tarifas, confirmación de tarifas, boletas y reportes. Estas comprobaciones no sustituyen pruebas completas de cada operación de escritura.

## Capturas

`docs/screenshots/` contiene imágenes reales de la aplicación local con datos ficticios. Para actualizarlas, ejecutar la demo, navegar a cada pantalla y capturar la vista sin incluir credenciales ni datos reales.
