# PROGRESO.md — Documentación técnica del proyecto

> Interfaz gráfica de control para una estación láser de nanoposicionamiento (mesas ANT130XY / ANT130LZS de Aerotech). Este documento describe la base tecnológica, la arquitectura y la organización del código, pensado como referencia para la memoria del TFG.

---

## 1. Resumen del proyecto

El proyecto es una aplicación de escritorio (GUI) que sirve de panel de control para una estación de posicionamiento láser de precisión. Permite:

- Ver en tiempo real la posición de los ejes X, Y, Z, el estado de seguridad (STO), la salud de cada eje (habilitado/homed/sin error/límites libres) y la consigna de salida del láser (página **Home**).
- Mover los ejes manualmente, paso a paso, con escala/velocidad/aceleración configurables (página **Manual**).
- Mover los ejes a una posición absoluta y programar el tiempo de apertura del *shutter* (página **Auto**).
- Cargar, editar y ejecutar programas G-Code (página **G-Code**).
- Configurar la conexión serie con el controlador (página **Connection**).
- Calibrar el enfoque en Z y poner a cero los ejes X/Y (página **Calibration**).
- Cambiar entre varios temas visuales (claro/oscuro/personalizados) desde un menú de ajustes.

El control real del hardware se hace a través de la API oficial **Aerotech Automation1** (paquete `automation1`), centralizada en `src/aerotech_controller.py`. Si no hay controlador físico disponible (p. ej. durante el desarrollo o la defensa del TFG sin la estación conectada), cada operación falla de forma controlada y se registra por consola, y la interfaz sigue funcionando con normalidad en modo simulado.

---

## 2. Stack tecnológico

| Elemento | Valor |
|---|---|
| Lenguaje | Python **3.12.4** |
| Framework GUI | **PySide6** 6.10.0 (bindings oficiales de Qt 6 para Python) |
| Librería de componentes | **QT-PyQt-PySide-Custom-Widgets** 1.0.2 (paquete `Custom_Widgets`) |
| Estilos | QSS (Qt Style Sheets) generado a partir de **SCSS/Sass** vía `qtsass` / `libsass` |
| Definición de interfaz | Escrita a mano en Python (sin `.ui` de Qt Designer) |
| Configuración de la app | JSON (`json-styles/style.json`) interpretado por `Custom_Widgets` |
| Sistema operativo objetivo | Windows |

### 2.1. Por qué PySide6 y no PyQt

El entorno tiene instaladas **ambas** familias de bindings de Qt (`PySide6` y `PyQt5`), pero todo el código de la aplicación importa exclusivamente `PySide6.*`. `PyQt5` queda como dependencia transitiva de la librería `Custom_Widgets` (que soporta varios bindings internamente a través de `QtPy`), no se usa directamente en el código propio.

---

## 3. Dependencias (entorno Python)

### 3.1. Utilizadas activamente por el código propio

| Paquete | Versión | Uso |
|---|---|---|
| `PySide6` / `PySide6-Essentials` / `PySide6-Addons` | 6.10.0 | Widgets, señales/slots, `QtCore`, `QtGui`, `QtWidgets`, `QtSerialPort` |
| `shiboken6` | 6.10.0 | Generador de *bindings* C++↔Python que usa PySide6 internamente |
| `QT-PyQt-PySide-Custom-Widgets` (`Custom_Widgets`) | 1.0.2 | Sistema de temas, menús deslizantes (`QCustomSlideMenu`), stacks animados (`QCustomQStackedWidget`), grupos de botones, overlays, iconografía coloreada por tema, compilación SCSS→QSS en caliente |
| `qtsass` | 0.4.0 | Compila los ficheros `.scss` de `Qss/scss` a CSS/QSS |
| `libsass` | 0.23.0 | Motor Sass usado por `qtsass` |
| `CairoSVG` / `cairocffi` / `pycairo` | 2.8.2 / 1.7.1 / 1.28.0 | Renderizado de los iconos SVG → PNG coloreados según el tema activo |
| `watchdog` | 6.0.0 | Recarga en caliente del QSS cuando cambian los `.scss` (`LiveCompileQss`) |
| `QtPy` | 2.4.3 | Capa de abstracción que usa `Custom_Widgets` para ser compatible con PyQt5/PyQt6/PySide2/PySide6 |

### 3.2. Instaladas para la integración con hardware (aún no activadas en el código)

| Paquete | Versión | Propósito previsto |
|---|---|---|
| `automation1` | 2.12.0 | SDK oficial de **Aerotech**, usado activamente en `src/aerotech_controller.py` para controlar el iSMC (drives iXC2e/XC2e de las mesas ANT130XY y ANT130LZS) |
| `PIPython` | 2.11.0.6 | SDK de **Physik Instrumente (PI)** para controladores de posicionamiento (no se usa; queda como alternativa/complemento de hardware) |
| `pyserial` | 3.5 | Comunicación serie de bajo nivel (no se usa directamente; la página Connection usa `QtSerialPort`) |
| `pyusb` | 1.3.1 | Comunicación USB de bajo nivel (no se usa actualmente) |

`automation1` es la única de estas cuatro que el código propio importa y utiliza (ver secciones 5.5 y 6.11). Las otras tres siguen instaladas en el entorno como posibles vías alternativas de comunicación con hardware, sin uso actual.

### 3.3. Dependencias indirectas relevantes

`matplotlib`, `numpy`, `pillow`, `lxml`, `fonttools`, `customtkinter`, `PyQt5` y otras aparecen en `pip freeze` como dependencias de `Custom_Widgets` o de otras librerías del entorno, pero no se importan desde el código propio del proyecto.

> El proyecto **no tiene** actualmente un `requirements.txt` ni `pyproject.toml`. Sería recomendable generar uno (`pip freeze > requirements.txt`, filtrando lo estrictamente necesario) para documentar el entorno de forma reproducible en la memoria del TFG.

---

## 4. Distribución del código (estructura de carpetas)

```
PyQt6_CodeOnly/
├── main.py                        # Punto de entrada de la aplicación
├── config.py                      # Flags de configuración globales (p. ej. LASER_INTERLOCK_AVAILABLE)
├── json-styles/
│   └── style.json                 # Configuración declarativa de la UI (temas, menús, botones...)
├── src/
│   ├── ui_interface.py            # Definición de TODOS los widgets (equivalente a un .ui "compilado" a mano)
│   ├── Functions.py               # Lógica transversal: fuentes, temas, conexión de botones de menú
│   ├── ui_extensions.py           # Orquestador de las extensiones de cada página
│   ├── aerotech_controller.py     # Gestor centralizado de la conexión con Aerotech Automation1-iSMC
│   ├── ui_extensions_home.py      # Lógica de la página Home
│   ├── ui_extensions_manual.py    # Lógica de la página Manual
│   ├── ui_extensions_auto.py      # Lógica de la página Auto
│   ├── ui_extensions_gcode.py     # Lógica de la página G-Code
│   ├── ui_extensions_connection.py# Lógica de la página Connection
│   └── ui_extensions_calibration.py# Lógica de la página Calibration
├── Qss/
│   ├── scss/                      # Fuente de estilos (Sass): main.scss, _styles.scss, _variables.scss (autogenerado)
│   └── icons/                     # Iconos SVG base + PNG coloreados generados por tema (feather, material_design, font_awesome)
├── images/                        # Imágenes estáticas (logotipos, fotos de la estación, gráficos)
├── generated-files/
│   ├── css/main.css               # QSS resultante de compilar el SCSS (se regenera en cada ejecución)
│   └── json/                      # Reservado por Custom_Widgets (vacío en este proyecto, ver sección 7)
├── logs/
│   └── custom_widgets.log         # Log interno de la librería Custom_Widgets
└── __pycache__/                   # Bytecode cacheado por Python (no versionar)
```

### 4.1. Tamaño del código propio (líneas de Python)

| Fichero | Líneas | Rol |
|---|---:|---|
| `src/ui_interface.py` | 2009 | Construcción de la interfaz (widgets, layouts, iconos, textos) |
| `src/ui_extensions_gcode.py` | 451 | Página G-Code + diálogo de edición + intérprete G-Code |
| `src/ui_extensions_auto.py` | 334 | Página Auto (movimiento absoluto + shutter temporizado) |
| `src/ui_extensions_manual.py` | 279 | Página Manual (jog manual + shutter) |
| `src/ui_extensions_connection.py` | 239 | Página Connection (puerto serie + conexión Aerotech) |
| `src/ui_extensions_home.py` | 296 | Página Home (banner conexión/STO, LEDs por eje, tarjeta de salida láser) |
| `src/aerotech_controller.py` | 337 | Envoltorio de la API automation1 (conexión, movimiento, E/S digital, fallos/homing/STO, potencia láser) |
| `src/ui_extensions_calibration.py` | 204 | Página Calibration |
| `src/Functions.py` | 103 | Fuentes, temas, señales de menú |
| `src/ui_extensions.py` | 90 | Orquestador de páginas + instancia compartida del controlador |
| `main.py` | 50 | Arranque de la aplicación |
| `config.py` | 12 | Flags de configuración globales |
| **Total** | **~4 404** | |

(No se cuentan los miles de ficheros `.png`/`.svg` de iconos ni las imágenes, que son binarios/recursos, no código.)

---

## 5. Arquitectura de la aplicación

### 5.1. Flujo de arranque (`main.py`)

```python
app = QApplication(sys.argv)
window = MainWindow()          # 1. Construye la ventana
window.show()
sys.exit(app.exec_())
```

Dentro de `MainWindow.__init__`:

1. **`Ui_MainWindow().setupUi(self)`** — construye todos los widgets de la ventana (definidos a mano en `ui_interface.py`, imitando lo que generaría Qt Designer + `pyside6-uic`).
2. **`loadJsonStyle(...)`** — lee `json-styles/style.json` y aplica: título/icono de ventana, temas disponibles, comportamiento de los menús deslizantes, grupos de botones, animaciones de los `QStackedWidget`, etc. (lo interpreta la librería `Custom_Widgets`).
3. **`UIExtensions(ui, self).apply_all_modifications()`** — aplica estilos y comportamiento específico de cada página (fuentes, tamaños, `QSS` en línea) que no cubre el JSON declarativo.
4. **`connect_all_signals()`** — conecta las señales (clics de botones, cambios de valores) a los métodos de cada página.
5. **`QAppSettings.updateAppSettings(self)`** — aplica el tema visual activo (compila el SCSS a QSS, aplica la paleta de colores, genera los iconos coloreados que falten).
6. **`GuiFunctions(self)`** — carga la tipografía de la app y rellena el selector de temas.

### 5.2. Patrón de organización: una clase "Extensions" por página

Cada página del `QStackedWidget` principal tiene su propia clase (`HomePageExtensions`, `ManualPageExtensions`, `AutoPageExtensions`, `GCodePageExtensions`, `ConnectionPageExtensions`, `CalibrationPageExtensions`), todas con la misma interfaz:

```python
class XxxPageExtensions:
    def __init__(self, ui, main_window): ...
    def apply_modifications(self):   # estilos, tamaños, textos iniciales
    def connect_signals(self):       # conexión de señales Qt (clics, cambios de valor...)
```

`UIExtensions` (en `ui_extensions.py`) instancia las seis clases y expone dos métodos de fachada (`apply_all_modifications`, `connect_all_signals`) que `main.py` invoca una sola vez. Esto separa **la interfaz generada** (`ui_interface.py`, no debería tocarse a mano salvo para regenerar) de **la lógica de cada pantalla** (los ficheros `ui_extensions_*.py`, donde se añade funcionalidad nueva).

### 5.3. Sistema de temas y estilos

- Los colores de cada tema (fondo, texto, acento, color de iconos) se definen declarativamente en `json-styles/style.json`, dentro de `QSettings → ThemeSettings → CustomTheme`. Actualmente hay 3 temas personalizados: **TIDE** (por defecto), **NEON** y **EMBER**, además de los temas `DARK`/`LIGHT` que añade la propia librería.
- `Custom_Widgets` traduce esas variables a un fichero `Qss/scss/_variables.scss`, que junto con `Qss/scss/_styles.scss` se compila a `generated-files/css/main.css` (el QSS real que se aplica a la aplicación) mediante `qtsass`.
- Con `"LiveCompileQss": true` en `style.json`, un `watchdog` vigila los `.scss` y recompila en caliente al guardarlos — útil durante el desarrollo del estilo visual.
- El cambio de tema en caliente lo gestiona `GuiFunctions.changeAppTheme()` (`src/Functions.py`), que guarda el tema elegido en `QSettings` y vuelve a aplicar el JSON.

### 5.4. Sistema de iconos

Los iconos (feather, material design y font-awesome) se distribuyen como **SVG base** dentro del propio paquete `Custom_Widgets`. En tiempo de ejecución, la librería:

1. Colorea cada SVG con el color de icono del tema activo (usando `cairosvg`) y lo exporta a PNG.
2. Guarda esos PNG en `Qss/icons/<color-del-tema-sin-#>/<estilo>/<nombre>.png` (p. ej. `Qss/icons/F7A618/feather/menu.png`).

Como la interfaz de este proyecto está escrita **a mano** (no generada desde Qt Designer + el plugin de `Custom_Widgets`), no existe el fichero de recursos compilado (`.qrc` → `_rc.py`) que normalmente resolvería las rutas `:/prefijo/icons/...`, ni el manifiesto `generated-files/json/*.json` que la librería usa para recolorear iconos automáticamente al cambiar de tema. Por eso `src/ui_interface.py` incluye una función auxiliar propia, `_icon_path()`, que traduce cada alias de icono a la ruta real en disco del PNG ya coloreado para el tema activo (leyendo el tema guardado en `QSettings`, con `json-styles/style.json` como valor por defecto).

### 5.5. Integración con hardware: Aerotech Automation1

El control real del sistema se hace a través del SDK oficial `automation1`, envuelto en una única clase, `AerotechController` (`src/aerotech_controller.py`), que **todas** las páginas comparten (`UIExtensions` la crea una vez y la pasa por constructor a cada `XxxPageExtensions`, en vez de que cada página abra su propia conexión o intente adivinar la de otra).

`AerotechController` expone:

- `connect(host)` / `disconnect()` / `is_connected` — conexión y arranque del controlador (`a1.Controller.connect(host).start()`). Por defecto se conecta a `"::1"` (localhost), el caso normal cuando la app corre en el mismo PC industrial que el iSMC.
- `get_axis_positions()` / `get_axes_enabled()` — lectura de posición y estado de los drives, vía `StatusItemConfiguration` + `runtime.status.get_status_items(...)` (la API real no expone el estado como atributos directos, hay que pedirlo explícitamente).
- `enable_axes()` / `disable_axes()` / `home_axes()` — habilitación y *homing* de los ejes (`runtime.commands.motion.enable/disable/home`).
- `move_relative(axis, distancia, vel, acc)` / `move_incremental(ejes, ...)` — movimiento relativo, vía `motion.moveincremental` (no `moverelative`, que no existe en la API real).
- `move_absolute(ejes, posiciones, vel, acc)` — movimiento absoluto, vía `motion.moveabsolute`, aplicando antes la rampa de aceleración con `motion_setup.setupaxisrampvalue(...)`.
- `zero_axis(axis, valor)` — fija el origen de coordenadas del eje en la posición actual (`motion.positionoffsetset`), usado por Calibration para las funciones "Zero X/Y" y "Set Z as calibrated".
- `set_digital_output(axis, output_num, valor)` — activa/desactiva una salida digital del drive; es lo que abre/cierra el shutter del láser desde la página Manual (`SHUTTER_OUTPUT_AXIS` / `SHUTTER_OUTPUT_NUM` en `ui_extensions_manual.py`, a ajustar según el cableado real de la estación).
- `get_axis_faults()` / `get_axes_homed()` / `get_sto_status(axis=None)` — añadidos en el rediseño de la página Home (sección 9) para alimentar los LEDs de estado por eje y el banner de STO. Leen `AxisFault`/`DriveStatus` vía el mismo `StatusItemConfiguration` ya usado para posición y habilitación. **Los nombres exactos de los bits (`AxisFault.PositionErrorFault`, `CwEndOfTravelLimitFault`, `CcwEndOfTravelLimitFault`, `DriveStatus.Homed`, y el bit de STO) están marcados con `# TODO` en el código: no se han verificado todavía contra la instalación real de `automation1` (`dir(a1.AxisFault)` / `dir(a1.DriveStatus)`).**
- `set_laser_power_percent(duty_percent)` / `get_laser_output_state()` — gestionan la consigna de potencia del láser (0-100% de duty cycle, convertido a mW usando `NEJE_B30635_MAX_POWER_MW = 500.0`). El canal PWM/TTL físico del NEJE **no está confirmado** (falta el documento *620D1426-10-01 System Interconnect*), así que `set_laser_power_percent()` solo guarda el valor en memoria y avisa por consola que corre en modo simulado; no escribe ninguna salida real todavía.

**Limitaciones conocidas y deliberadas:**

- `home_axes()` es una llamada **bloqueante** de la API (espera a que termine el ciclo de homing) y se ejecuta en el hilo de la interfaz: mientras dura, la ventana no responde. Para producción convendría moverla a un `QThread`.
- `Controller.connect()` también es bloqueante y, sin hardware escuchando en el host indicado, puede tardar **más de un minuto** en fallar (comprobado empíricamente). Por eso la conexión **no** se intenta automáticamente al arrancar la app: se dispara solo cuando el usuario pulsa "Connect" en la página Connection, y esa pulsación lanza la conexión en un `QThread` aparte (`_ConnectWorker` en `ui_extensions_connection.py`) para no congelar la interfaz mientras se resuelve.
- El tiempo de apertura del shutter que se guarda en la página Auto (`acceptBtn`) **no** se envía a un temporizador PSO (Position Synchronized Output) del drive: hacerlo correctamente exige configurar una ventana PSO específica del cableado de la estación (eje, salida, modo distancia/tiempo) que no está definida en este proyecto. El valor queda guardado (`_saved_shutter_time_s`) para una futura secuencia automática que abra/cierre el shutter por software combinando `set_digital_output(...)` con un `QTimer`.
- El intérprete de G-Code (`GCodePageExtensions`) ejecuta cada línea de forma síncrona; un `G28` (home) a mitad de programa congela la UI por el mismo motivo que el punto anterior.

---

## 6. Descripción módulo por módulo

### 6.1. `main.py`
Punto de entrada. Crea la `QApplication`, instancia `MainWindow` y arranca el bucle de eventos de Qt. La inicialización del controlador Aerotech ya no vive aquí: la gestiona `UIExtensions` (ver 6.4 y 6.11).

### 6.2. `src/ui_interface.py`
Clase `Ui_MainWindow`, con un único método `setupUi()` que crea y posiciona **todos** los widgets de la aplicación: cabecera personalizada (sin barra de título nativa — ventana *frameless*), menú lateral, menús deslizantes central/derecho, y el `QStackedWidget` principal con las 6 páginas funcionales (`homePage`, `manualPage`, `autoPage`, `gcodePage`, `connectionPage`, `calibrationPage`) más las páginas de ajustes (`settingsPage`, `helpPage`). Incluye también la función auxiliar `_icon_path()` descrita en el punto 5.4.

### 6.3. `src/Functions.py`
Clase `GuiFunctions`. Se encarga de:
- Cargar la tipografía personalizada de la app (`ProductSans-Regular.ttf`).
- Inicializar y poblar el selector de temas (excluyendo los temas internos `DARK`/`LIGHT`).
- Conectar los botones que abren/cierran los menús deslizantes central y derecho (Settings/Help/Connection/Calibration).
- Cambiar el tema activo cuando el usuario elige uno distinto en el desplegable.

### 6.4. `src/ui_extensions.py`
Clase `UIExtensions`: orquestador central descrito en el punto 5.2. Crea la única instancia de `AerotechController` y la reparte por constructor a las seis páginas. También aplica la fuente global (`Sitka Small`) a toda la ventana y la fuente de título en negrita a los encabezados de cada sección.

### 6.5. `src/ui_extensions_home.py`
Página de estado general, rediseñada en agosto de 2026 (ver sección 9). Muestra:
- Un **banner superior** de conexión (IP del host) y de STO (Safe Torque Off), que pasa a rojo de alerta fijo cuando el STO está activo.
- Posición X/Y/Z, mostrando "—" en gris atenuado en vez de "0.000" cuando no hay conexión (para no confundir "en el origen" con "desconectado").
- 4 LEDs por eje (Habilitado, Homed, Sin error de posición, Límites libres), construidos con el helper único `_make_led()`.
- Una tarjeta **"Salida Láser"** (`laserOutputCard`, fusión de las antiguas `shutterStatus`/`powerStatus`) con LED ON/OFF, consigna de potencia (`estadoPotencia`, siempre con el sufijo "(consigna)" para dejar claro que no es una medida real) y un slot de interlock (gris fijo mientras `config.LASER_INTERLOCK_AVAILABLE` sea `False`).

Un `QTimer` de 100 ms refresca todo el estado llamando a `controller.get_axis_positions()`, `get_axes_enabled()`, `get_axes_homed()`, `get_axis_faults()`, `get_sto_status()` y `get_laser_output_state()`.

### 6.6. `src/ui_extensions_manual.py`
Movimiento manual paso a paso en X/Y/Z (vía `controller.move_relative`) con selector de escala (nm/μm/mm/cm), velocidad y aceleración configurables, y control del *shutter* (abrir/cerrar, mutuamente excluyentes, vía `controller.set_digital_output`).

### 6.7. `src/ui_extensions_auto.py`
Movimiento a posición absoluta (X/Y/Z en mm, vía `controller.move_absolute`) con los mismos parámetros de velocidad/aceleración que la página Manual, sincronizados bidireccionalmente entre ambas páginas. El botón Reset manda los tres ejes a *home* (`controller.home_axes`). Incluye la configuración del tiempo de apertura del *shutter* con selector de unidad temporal (ns/μs/ms/s) — guardado para un futuro disparo temporizado por software (ver limitaciones en 5.5).

### 6.8. `src/ui_extensions_gcode.py`
Carga de ficheros G-Code por diálogo o arrastrar-y-soltar (*drag & drop*), editor de texto integrado (`GCodeEditorDialog`) y un intérprete línea a línea que soporta `G0`/`G1` (movimiento, absoluto o relativo según `G90`/`G91`), `G28` (home) y `M0` (pausa: deshabilita los ejes), traduciendo cada línea a llamadas de `AerotechController`.

### 6.9. `src/ui_extensions_connection.py`
Selector de puerto serie (usa `QSerialPortInfo` de `PySide6.QtSerialPort` para listar los puertos disponibles del sistema) y de *baud rate*, pensado para un posible dispositivo serie auxiliar (el iSMC de Aerotech no se conecta por COM/baudios). El botón "Connect" lanza `AerotechController.connect()` en un `QThread` (clase interna `_ConnectWorker`) para no bloquear la interfaz mientras se resuelve la conexión.

### 6.10. `src/ui_extensions_calibration.py`
Calibración de enfoque en Z (subir/bajar en pasos de `FOCUS_STEP_MM` vía `controller.move_relative`, confirmar con `controller.zero_axis`) y puesta a cero de las posiciones X e Y (`controller.zero_axis`).

### 6.11. `src/aerotech_controller.py`
Clase `AerotechController`: envoltorio único sobre el SDK `automation1`, descrito en detalle en el punto 5.5. Es el único módulo que importa `automation1` directamente; el resto de páginas solo llaman a sus métodos.

---

## 7. Estado actual y trabajo pendiente

- **Integración de hardware real**: implementada y con la sintaxis verificada contra el SDK `automation1` instalado (`Controller.connect/start`, `StatusItemConfiguration`, `motion.moveincremental/moveabsolute/home`, `motion_setup.setupaxisrampvalue`, `io.digitaloutputset`). Sin la estación física conectada, cada operación se prueba en modo "sin conexión" (falla de forma controlada, registrada por consola); falta la validación final con el iSMC real en el laboratorio.
- **Shutter temporizado por hardware (PSO)**: no implementado — ver limitación detallada en 5.5. El valor introducido en la página Auto se guarda pero no dispara nada por sí solo todavía.
- **Llamadas bloqueantes en el hilo de la UI**: `home_axes()` y la ejecución de G-Code síncrona pueden congelar la ventana mientras esperan al controlador. Solo la conexión inicial (`Connect`) se ejecuta ya en un `QThread`; home/G-Code quedarían pendientes de la misma mejora si se usan con hardware real conectado.
- **Salida digital del shutter sin calibrar**: `SHUTTER_OUTPUT_AXIS`/`SHUTTER_OUTPUT_NUM` (en `ui_extensions_manual.py` y `ui_extensions_auto.py`) son valores por defecto (`AXIS_X`, `0`) que hay que ajustar al cableado real de la estación.
- **Sin control de versiones**: el directorio de trabajo no es (todavía) un repositorio Git.
- **Sin fichero de dependencias**: falta un `requirements.txt`/`pyproject.toml` para fijar versiones y facilitar la reproducibilidad del entorno.
- **Ruta de fuente tipográfica**: `Functions.py` carga la fuente desde `.fonts/google-sans-cufonfonts/ProductSans-Regular.ttf`, carpeta que no existe actualmente en el proyecto (falla de forma silenciosa y Qt usa una fuente de reemplazo).
- **Bits de estado sin verificar**: `get_axis_faults()`, `get_axes_homed()` y `get_sto_status()` (nuevos, ver sección 9) asumen nombres de bit de `a1.AxisFault`/`a1.DriveStatus` que no se han contrastado todavía contra la instalación real del SDK — marcado con `# TODO` en `aerotech_controller.py`.
- **Interlock del láser**: el LED de interlock de la tarjeta "Salida Láser" existe en la interfaz pero se mantiene en gris fijo (`config.LASER_INTERLOCK_AVAILABLE = False`) hasta confirmar la señal en el interconnect real.
- **Canal PWM del láser**: `set_laser_power_percent()` guarda la consigna en memoria pero no escribe sobre ninguna salida física; falta el documento de interconexión para saber a qué eje/salida está cableado el pin TTL/PWM del NEJE B30635.

---

## 8. Cómo ejecutar el proyecto

```bash
python main.py
```

Requiere Python 3.12 y las dependencias listadas en la sección 3 instaladas en el entorno (`pip install PySide6 QT-PyQt-PySide-Custom-Widgets qtsass libsass cairosvg watchdog`, como mínimo, para la parte de interfaz/temas). El primer arranque tras cambiar de tema puede tardar unos segundos mientras `Custom_Widgets` genera en segundo plano los iconos coloreados que falten.

---

## 9. Rediseño de la página Home (2026-08-14)

Cambio de alcance acotado a la página **Home** (`src/ui_interface.py`, `src/ui_extensions_home.py`) y a las adiciones necesarias en `src/aerotech_controller.py` / `config.py` para soportarla. No se ha tocado Manual, Auto, G-Code, Connection ni Calibration.

### 9.1. Motivación

La página Home mezclaba dos problemas: (1) el estado del *shutter* se inferían de la habilitación de los ejes, algo que no tiene relación real con si el láser está emitiendo; y (2) no había forma de distinguir, de un vistazo, "eje en el origen (0.000)" de "sin conexión con el controlador", ni ningún indicador de seguridad (STO) o de salud por eje (homed, límites, error de posición).

### 9.2. Cambios de interfaz (`src/ui_interface.py`)

- **Tarjetas fusionadas**: `shutterStatus` y `powerStatus` (y sus widgets internos `label_18`, `label`, `estadoOn`, `estadoOff`, `label_30`, `label_34`, `estadoPower`) desaparecen. En su lugar, una única tarjeta `laserOutputCard` con icono, título "Salida Láser:", LED + texto ON/OFF, campo de solo lectura `estadoPotencia` (formato `"{duty:.0f}% · {mw:.0f} mW (consigna)"`, con el sufijo "(consigna)" siempre presente) y un slot de interlock (LED + texto "Interlock: N/D").
- **Banner superior** (`statusBanner`, primer elemento de la página, alto 40-48 px): LED + texto de conexión ("Conectado — `<host>`" / "Desconectado") a la izquierda, LED + texto de STO ("Seguridad OK" / "STO ACTIVO") a la derecha. El fondo del banner cambia a `#DA190B` (rojo fijo, no ligado al tema) cuando el STO está activo.
- **LEDs de estado por eje**: bajo cada línea de posición (X/Y/Z) se añadió una fila con 4 LEDs de 12×12 px (Habilitado, Homed, Sin error de posición, Límites libres), cada uno con `toolTip` del nombre completo.
- Para insertar el banner sin romper el layout horizontal existente de `homePage`, su layout raíz pasó de `QHBoxLayout` (`horizontalLayout_18`, aplicado directamente sobre `homePage`) a un `QVBoxLayout` nuevo (`verticalLayout_home`) que contiene el banner arriba y el antiguo `horizontalLayout_18` (ahora un sub-layout, sin cambios internos) debajo.
- Se actualizó el selector SCSS `QFrame#shutterStatus,#powerStatus` de `Qss/scss/defaultStyle.scss` a `QFrame#laserOutputCard`, para que la tarjeta fusionada conserve el mismo fondo/borde de "card" que tenían las dos originales (único cambio en el sistema de temas; no se tocaron paletas de color ni `style.json`).

### 9.3. Cambios de lógica (`src/ui_extensions_home.py`)

- Nuevo método `_make_led(color, size, tooltip)`: única factoría para los 16 LEDs de la página (12 de eje + ON/OFF + interlock + 2 del banner), evita repetir la construcción del indicador. Todos son `QFrame` circulares (no `QLineEdit`, a diferencia del `estadoOn`/`estadoOff` original).
- `update_position_display()` reescrito: si `controller.is_connected` es `False`, pinta "—" en gris (`#999999`) en X/Y/Z, todos los LEDs en gris y el banner en "Desconectado", sin leer ningún otro estado. Si hay conexión, además de la posición lee `get_axes_enabled()`, `get_axes_homed()`, `get_axis_faults()`, `get_sto_status()` y `get_laser_output_state()`.
- Eliminados `update_shutter_display(is_open)` y el uso de `get_axes_enabled()` como proxy del estado del shutter (lógica incorrecta); sustituidos por la tarjeta "Salida Láser", alimentada por `get_laser_output_state()`.
- Nota de implementación: como `get_axes_enabled()` devuelve un único booleano combinado para los 3 ejes (no hay lectura individual por eje en la API), el LED "Habilitado" de X, Y y Z muestra ese mismo valor combinado — no hay 3 lecturas independientes.
- El `QTimer` de 100 ms se mantiene sin cambios (no se ha migrado el polling a un `QThread` en esta fase).

### 9.4. Cambios en `src/aerotech_controller.py` y `config.py`

Ver detalle en las secciones 5.5, 6.11 y 7. Resumen: se añadieron `get_axis_faults()`, `get_axes_homed()`, `get_sto_status(axis=None)`, `set_laser_power_percent(duty_percent)`, `get_laser_output_state()` y la constante `NEJE_B30635_MAX_POWER_MW`, sin eliminar ni modificar el comportamiento de ningún método existente. Se creó `config.py` con el flag `LASER_INTERLOCK_AVAILABLE = False`.

### 9.5. Pendiente / no implementado en esta fase

- Verificar contra la instalación real de `automation1` los nombres de bit usados en `get_axis_faults()`, `get_axes_homed()` y `get_sto_status()` (marcados con `# TODO` en el código).
- Confirmar el canal PWM/TTL físico del láser NEJE B30635 contra el documento *620D1426-10-01 System Interconnect* y conectar `set_laser_power_percent()` a la salida real.
- Confirmar la señal de interlock en el interconnect y activar `config.LASER_INTERLOCK_AVAILABLE`.
- Migración de las páginas Manual/Auto/G-Code del antiguo `set_digital_output` del shutter al nuevo esquema de PWM/láser (fuera de alcance de este cambio).
