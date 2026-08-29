# PROGRESO.md — Documentación técnica del proyecto

> Interfaz gráfica de control para una estación láser de nanoposicionamiento (mesas ANT130XY / ANT130LZS de Aerotech). Este documento describe la base tecnológica, la arquitectura y la organización del código, pensado como referencia para la memoria del TFG.

---

## 1. Resumen del proyecto

El proyecto es una aplicación de escritorio (GUI) que sirve de panel de control para una estación de posicionamiento láser de precisión. Permite:

- Ver en tiempo real, desde un **panel de estado global** visible en Home/Manual/Auto, la conexión con el iSMC, el estado de seguridad (STO), la posición X/Y/Z y la salud de cada eje (Enabled/Homed/In Position/No limit active).
- Ver el estado de la salida del láser (ON/OFF, consigna de potencia) junto a la imagen de la estación (página **Home**).
- Mover los ejes manualmente, paso a paso, con escala/velocidad configurables, habilitación/homing independiente por eje, y disparar el láser en PSO real mientras se mantiene pulsado "Laser ON" (página **Manual**).
- Generar G-Code automáticamente en 5 modos (Single point, Fixed-distance firing, Point array, Power gradient, Binary pattern), con vista previa en vivo y exportación a la página G-Code o a fichero (página **Auto**).
- Cargar, editar y ejecutar programas G-Code — dialecto ampliado con `G4`/`M3`/`M5`/`M900`/`M901` para disparo PSO — con vista previa de solo lectura (página **G-Code**).
- Configurar la conexión por IP con el controlador, con validación de formato y persistencia local de la última IP exitosa (página **Connection**).
- Calibrar el enfoque en Z (con lectura en vivo y confirmación manual), definir una ventana maestra de seguridad X/Y por dos esquinas, y alinear el láser en un modo de potencia limitada (página **Calibration**).
- Cambiar entre varios temas visuales (claro/oscuro/personalizados) desde un menú de ajustes.

El control real del hardware se hace a través de la API oficial **Aerotech Automation1** (paquete `automation1`), centralizada en `src/aerotech_controller.py`, incluyendo una capa PSO (Position Synchronized Output) dedicada al láser NEJE B30635. Si no hay controlador físico disponible (p. ej. durante el desarrollo o la defensa del TFG sin la estación conectada), cada operación falla de forma controlada y se registra por consola, y la interfaz sigue funcionando con normalidad en modo simulado.

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

`automation1` es la única de estas cuatro que el código propio importa y utiliza (ver secciones 5.5 y 6.9). Las otras tres siguen instaladas en el entorno como posibles vías alternativas de comunicación con hardware, sin uso actual.

### 3.3. Dependencias indirectas relevantes

`matplotlib`, `numpy`, `pillow`, `lxml`, `fonttools`, `customtkinter`, `PyQt5` y otras aparecen en `pip freeze` como dependencias de `Custom_Widgets` o de otras librerías del entorno, pero no se importan desde el código propio del proyecto.

> El proyecto **no tiene** actualmente un `requirements.txt` ni `pyproject.toml`. Sería recomendable generar uno (`pip freeze > requirements.txt`, filtrando lo estrictamente necesario) para documentar el entorno de forma reproducible en la memoria del TFG.

---

## 4. Distribución del código (estructura de carpetas)

```
PyQt6_CodeOnly/
├── main.py                        # Punto de entrada: MainWindow + UIExtensions + GuiFunctions (ver sección 11)
├── config.py                      # Flags de configuración globales (p. ej. LASER_INTERLOCK_AVAILABLE)
├── json-styles/
│   └── style.json                 # Configuración declarativa de la UI (temas, menús, botones...)
├── src/
│   ├── ui_interface.py            # Definición de TODOS los widgets (equivalente a un .ui "compilado" a mano)
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
| `src/ui_interface.py` | 2201 | Construcción de la interfaz (widgets, layouts, iconos, textos) |
| `main.py` | 490 | Arranque + `GlobalStatusPanel` + orquestador de páginas (`UIExtensions`) + fuentes/temas/menú (`GuiFunctions`) |
| `src/ui_extensions_gcode.py` | 613 | Página G-Code + diálogo de edición + intérprete G-Code (G0/G1/G4/G28/G90/G91/M0/M3/M5/M900/M901) |
| `src/ui_extensions_auto.py` | 482 | Página Auto — generador de G-Code en 5 modos |
| `src/ui_extensions_manual.py` | 425 | Página Manual (jog manual, control por eje, láser en PSO por mantener-pulsado) |
| `src/aerotech_controller.py` | 429 | Envoltorio de la API automation1 (conexión, movimiento, indicadores por eje, STO, capa PSO) |
| `src/ui_extensions_calibration.py` | 430 | Página Calibration (foco Z, ventana maestra de seguridad, modo de alineación láser) |
| `src/ui_extensions_connection.py` | 223 | Página Connection (IP del iSMC, validación, persistencia local) |
| `src/ui_extensions_home.py` | 150 | Página Home (tarjeta de salida láser + imagen de la estación) |
| `config.py` | 29 | Flags de configuración globales |
| **Total** | **~5 472** | |

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
3. **`self.controller = AerotechController()`** — única instancia, creada aquí (no dentro de `UIExtensions`) para poder compartirla también con `GlobalStatusPanel`.
4. **`GlobalStatusPanel(self.controller, self)`** — se construye e inserta encima de `mainPages`; se conecta su visibilidad a `mainPages.currentChanged` y arranca el `QTimer` de 100 ms que lo refresca (ver sección 12).
5. **`UIExtensions(ui, self, self.controller).apply_all_modifications()`** — aplica estilos y comportamiento específico de cada página (fuentes, tamaños, `QSS` en línea) que no cubre el JSON declarativo.
6. **`connect_all_signals()`** — conecta las señales (clics de botones, cambios de valores) a los métodos de cada página, y conecta `GlobalStatusPanel.laser_emergency_stop` al slot de parada de Manual.
7. **`QAppSettings.updateAppSettings(self)`** — aplica el tema visual activo (compila el SCSS a QSS, aplica la paleta de colores, genera los iconos coloreados que falten).
8. **`GuiFunctions(self)`** — carga la tipografía de la app y rellena el selector de temas.

`UIExtensions` y `GuiFunctions` viven en el propio `main.py`, debajo de `MainWindow` (consolidación de agosto de 2026, sección 11) — igual que `GlobalStatusPanel` (sección 12), añadida ahí mismo por instrucción explícita de las directrices de migración ("construido en `main.py`, junto al resto de widgets raíz").

### 5.2. Patrón de organización: una clase "Extensions" por página

Cada página del `QStackedWidget` principal tiene su propia clase (`HomePageExtensions`, `ManualPageExtensions`, `AutoPageExtensions`, `GCodePageExtensions`, `ConnectionPageExtensions`, `CalibrationPageExtensions`), todas con la misma interfaz:

```python
class XxxPageExtensions:
    def __init__(self, ui, main_window, controller): ...
    def apply_modifications(self):   # estilos, tamaños, textos iniciales
    def connect_signals(self):       # conexión de señales Qt (clics, cambios de valor...)
```

`UIExtensions` (en `main.py`) instancia las seis clases — pasándoles el `AerotechController` que ya crea `MainWindow`, no uno propio — y expone dos métodos de fachada (`apply_all_modifications`, `connect_all_signals`) que `MainWindow.__init__` invoca una sola vez. Esto separa **la interfaz generada** (`ui_interface.py`, no debería tocarse a mano salvo para regenerar) de **la lógica de cada pantalla** (los ficheros `ui_extensions_*.py`, donde se añade funcionalidad nueva), del **estado compartido entre páginas** (`GlobalStatusPanel`, en `main.py`) y del **arranque/orquestación** (`main.py`).

### 5.3. Sistema de temas y estilos

- Los colores de cada tema (fondo, texto, acento, color de iconos) se definen declarativamente en `json-styles/style.json`, dentro de `QSettings → ThemeSettings → CustomTheme`. Actualmente hay 3 temas personalizados: **TIDE** (por defecto), **NEON** y **EMBER**, además de los temas `DARK`/`LIGHT` que añade la propia librería.
- `Custom_Widgets` traduce esas variables a un fichero `Qss/scss/_variables.scss`, que junto con `Qss/scss/_styles.scss` se compila a `generated-files/css/main.css` (el QSS real que se aplica a la aplicación) mediante `qtsass`.
- Con `"LiveCompileQss": true` en `style.json`, un `watchdog` vigila los `.scss` y recompila en caliente al guardarlos — útil durante el desarrollo del estilo visual.
- El cambio de tema en caliente lo gestiona `GuiFunctions.changeAppTheme()` (clase definida en `main.py`), que guarda el tema elegido en `QSettings` y vuelve a aplicar el JSON.

### 5.4. Sistema de iconos

Los iconos (feather, material design y font-awesome) se distribuyen como **SVG base** dentro del propio paquete `Custom_Widgets`. En tiempo de ejecución, la librería:

1. Colorea cada SVG con el color de icono del tema activo (usando `cairosvg`) y lo exporta a PNG.
2. Guarda esos PNG en `Qss/icons/<color-del-tema-sin-#>/<estilo>/<nombre>.png` (p. ej. `Qss/icons/F7A618/feather/menu.png`).

Como la interfaz de este proyecto está escrita **a mano** (no generada desde Qt Designer + el plugin de `Custom_Widgets`), no existe el fichero de recursos compilado (`.qrc` → `_rc.py`) que normalmente resolvería las rutas `:/prefijo/icons/...`, ni el manifiesto `generated-files/json/*.json` que la librería usa para recolorear iconos automáticamente al cambiar de tema. Por eso `src/ui_interface.py` incluye una función auxiliar propia, `_icon_path()`, que traduce cada alias de icono a la ruta real en disco del PNG ya coloreado para el tema activo (leyendo el tema guardado en `QSettings`, con `json-styles/style.json` como valor por defecto).

### 5.5. Integración con hardware: Aerotech Automation1

El control real del sistema se hace a través del SDK oficial `automation1`, envuelto en una única clase, `AerotechController` (`src/aerotech_controller.py`), que **todas** las páginas comparten (`UIExtensions`, en `main.py`, la crea una vez y la pasa por constructor a cada `XxxPageExtensions`, en vez de que cada página abra su propia conexión o intente adivinar la de otra).

`AerotechController` expone:

- `connect(host)` / `disconnect()` / `is_connected` — conexión y arranque del controlador (`a1.Controller.connect(host).start()`). El valor por defecto (`"192.168.7.1"`) no se toca; la página Connection ahora lo precarga en `hostAddressInput` en vez de fijarlo aquí (ver 6.7).
- `get_axis_positions()` — lectura de posición vía `StatusItemConfiguration` + `runtime.status.get_status_items(...)` (la API real no expone el estado como atributos directos, hay que pedirlo explícitamente).
- `enable_axes()` / `disable_axes()` / `home_axes()` — habilitación y *homing* de los ejes (`runtime.commands.motion.enable/disable/home`).
- `move_relative(axis, distancia, vel, acc)` / `move_incremental(ejes, ...)` — movimiento relativo, vía `motion.moveincremental` (no `moverelative`, que no existe en la API real).
- `move_absolute(ejes, posiciones, vel, acc)` — movimiento absoluto, vía `motion.moveabsolute`, aplicando antes la rampa de aceleración con `motion_setup.setupaxisrampvalue(...)`.
- `zero_axis(axis, valor)` — fija el origen de coordenadas del eje en la posición actual (`motion.positionoffsetset`), usado por Calibration para "Zero X/Y" y "Confirm focus".
- `set_digital_output(axis, output_num, valor)` — activa/desactiva una salida digital del drive. Ya **no se usa para el láser** (sustituido por la capa PSO, ver abajo); queda disponible para otras salidas no relacionadas.
- `get_axis_indicators(axis)` — **añadido en la migración de agosto de 2026** (sección 12), sustituye a las antiguas `get_axes_enabled()`/`get_axes_homed()`/`get_axis_faults()`. Devuelve `{"enabled", "homed", "in_position", "no_limit_active"}` **por eje individual** (la vieja `get_axes_enabled()` devolvía un único booleano combinado para los 3 ejes — esa limitación, señalada en las secciones 9.3/10.2, queda resuelta de raíz). **`# TODO` en el código:** los nombres de bit de `AxisStatus`/`DriveStatus`/`AxisFault` (`in_position` en particular) no se han verificado contra la instalación real.
- `get_sto_status(axis=None)` — sin cambios desde la fase de Home.
- **Capa PSO** (Position Synchronized Output), añadida en agosto de 2026 para el láser NEJE B30635 (cableado a la salida PSO dedicada del drive 1 / eje X): `pso_reset(axis)`, `pso_configure_fixed_distance(axis, distance_mm)`, `pso_configure_array_distances(axis, distances_mm)`, `pso_configure_waveform(axis, power_percent, total_time_us=20000, pulse_count=1)` (también actualiza `self._laser_duty_cycle`), `pso_configure_window(axis, window_number, min_mm, max_mm, as_mask)`, `pso_configure_bitmap(axis, bits)`, `pso_output_on(axis)` / `pso_output_off(axis)`. **`# TODO` en el código:** namespace y nombres de método sin confirmar contra la API instalada — `runtime.commands.pso.*` es el namespace probable, pero no verificado (los ejemplos oficiales de Aerotech son para la familia XC4, no necesariamente literales en XC2e/iXC2e).
- `set_laser_power_percent(duty_percent)` — ya **no se llama desde ninguna página** (Manual y Calibration usan `pso_configure_waveform()` en su lugar), pero se mantiene definida sin cambios.
- `get_laser_output_state()` — ahora devuelve **4 valores**: `(is_on, duty_percent, power_mw, is_measured)`. `is_measured` cae siempre a `False` (**`# TODO`**: falta leer el bit `OutputActive` real del estado PSO); `is_on`/`duty_percent` siguen derivándose de `self._laser_duty_cycle`.

**Limitaciones conocidas y deliberadas:**

- `home_axes()` es una llamada **bloqueante** de la API (espera a que termine el ciclo de homing) y se ejecuta en el hilo de la interfaz: mientras dura, la ventana no responde. Para producción convendría moverla a un `QThread`.
- `Controller.connect()` también es bloqueante y, sin hardware escuchando en el host indicado, puede tardar **más de un minuto** en fallar (comprobado empíricamente). Por eso la conexión **no** se intenta automáticamente al arrancar la app: se dispara solo cuando el usuario pulsa "Connect" en la página Connection, y esa pulsación lanza la conexión en un `QThread` aparte (`_ConnectWorker` en `ui_extensions_connection.py`) para no congelar la interfaz mientras se resuelve.
- El intérprete de G-Code (`GCodePageExtensions`) ejecuta cada línea de forma síncrona, incluyendo el nuevo `G4` (dwell, usa `time.sleep()`); un `G28` o un `G4` largo a mitad de programa congela la UI por el mismo motivo.
- El generador de G-Code de Auto (`Point array` con espaciado "Irregular", `Binary pattern`) no tiene todavía un M-code propio en el dialecto de G-Code para distancias no uniformes ni patrones de bits — se aproximan con `M900`/comentarios hasta decidir cómo ampliar el dialecto (ver sección 12).

---

## 6. Descripción módulo por módulo

### 6.1. `main.py`
Punto de entrada, y desde agosto de 2026 también el archivo que reúne el arranque, el panel de estado compartido y las clases de orquestación:
- **`GlobalStatusPanel`** (nuevo, ver sección 12) — `QFrame` construido una vez en `MainWindow.__init__`, insertado fuera del `QStackedWidget` principal (encima de `mainPages`, dentro de `verticalLayout_11`). Muestra el banner de conexión/STO, la posición X/Y/Z en vivo, la matriz de LEDs ENA/HMD/INP/LIM por eje y el botón "LASER STOP". Visible solo en Home/Manual/Auto (`MainWindow._update_global_panel_visibility`, conectado a `mainPages.currentChanged`). Refrescado por un único `QTimer` de 100 ms propiedad de `MainWindow`.
- **`MainWindow`** — crea la `QApplication`, instancia la ventana, el `AerotechController` compartido y el `GlobalStatusPanel`, y arranca el bucle de eventos de Qt.
- **`UIExtensions`** — orquestador central descrito en el punto 5.2. Recibe el `AerotechController` ya creado por `MainWindow` (no lo crea) y lo reparte por constructor a las seis páginas.
- **`GuiFunctions`** — carga la tipografía personalizada de la app, inicializa y puebla el selector de temas, conecta los botones que abren/cierran los menús deslizantes central y derecho.

### 6.2. `src/ui_interface.py`
Clase `Ui_MainWindow`, con un único método `setupUi()` que crea y posiciona **todos** los widgets de la aplicación: cabecera personalizada (sin barra de título nativa — ventana *frameless*), menú lateral, menús deslizantes central/derecho, y el `QStackedWidget` principal con las 6 páginas funcionales (`homePage`, `manualPage`, `autoPage`, `gcodePage`, `connectionPage`, `calibrationPage`) más las páginas de ajustes (`settingsPage`, `helpPage`). Incluye también la función auxiliar `_icon_path()` descrita en el punto 5.4.

### 6.3. `src/ui_extensions_home.py`
Simplificada drásticamente en la migración de agosto de 2026 (sección 12): la mayor parte de lo que tenía (banner, matriz de LEDs, posición) se trasladó a `GlobalStatusPanel`. Lo único que queda es la tarjeta **"Laser Output"** (`laserOutputCard`, LED ON/OFF con borde punteado si el valor no es medido, consigna `"{duty:.0f}% · {mw:.0f} mW (setpoint)"`) junto a la imagen de la estación (`estacionAerotech`), uno al lado del otro. Un `QTimer` propio y ligero (100 ms) refresca solo esta tarjeta vía `controller.get_laser_output_state()` — ya no lee posición, eso lo hace el timer de `GlobalStatusPanel`.

### 6.4. `src/ui_extensions_manual.py`
Movimiento manual paso a paso en X/Y/Z (vía `controller.move_relative`), reescrita en la migración de agosto de 2026:
- **Control por eje** (`axisControlManual`, se mantiene): Enable/Disable/Home por eje — ya no tiene LEDs propios (están en `GlobalStatusPanel`).
- **Solo velocity** (sin aceleración visible): la aceleración usa `config.DEFAULT_ACCELERATION_MM_S2[axis]`, fija. `velocity` mantiene la compuerta de confirmación (borde naranja + `confirmBtn`).
- **Láser en PSO real, mantener pulsado**: `laserPowerSlider` solo fija una consigna visual (ya no llama a `set_laser_power_percent()`); `laserFireBtn` ("Laser ON") dispara mientras se mantiene pulsado (`pressed`/`released`) vía `controller.pso_configure_waveform()` + `pso_output_on()`/`pso_output_off()`. `handle_emergency_stop()` está conectado a `GlobalStatusPanel.laser_emergency_stop`.

### 6.5. `src/ui_extensions_auto.py`
Reescrita por completo (antes: movimiento absoluto + *shutter* temporizado — todo eliminado). Ahora es un **generador de G-Code** con 5 modos (`modeSelector` + `modeStack`): Single point, Fixed-distance firing, Point array (con lista de pasadas `Add pass`/`Remove pass`), Power gradient (Linear/Radial, siempre segmentado en G1+M3) y Binary pattern. Cada modo tiene su propio panel de campos; cualquier cambio regenera en vivo la vista previa (`gcodePreviewAuto`), que siempre empieza y termina en `G28`. "Open in G-Code" llama a `gcode_ext.load_gcode_text()`; "Download file" exporta a `.gcode`. Tiene su propio control por eje (`axisControlAuto`, no comparte widgets con Manual).

### 6.6. `src/ui_extensions_gcode.py`
Carga de ficheros G-Code por diálogo o arrastrar-y-soltar (*drag & drop*), editor de texto integrado (`GCodeEditorDialog`), un panel de vista previa de solo lectura (`gcodePreview`, junto al drag-and-drop) y un intérprete línea a línea. Dialecto ampliado en agosto de 2026: `G0`/`G1` (movimiento), `G4 P<ms>` (dwell, bloqueante), `G28` (home), `G90`/`G91` (absoluto/relativo), `M0` (pausa), `M3 S<0-100>`/`M5` (PSO on/off), `M900 D<mm> P<pulsos>` (distancia fija PSO) y `M901 X<min> X<max> Y<min> Y<max>` (ventana PSO, validada contra la ventana maestra de Calibration). `load_gcode_text(text)` permite cargar G-Code directamente desde Auto sin pasar por fichero.

### 6.7. `src/ui_extensions_connection.py`
Reescrita en agosto de 2026: el selector de puerto serie/baud rate (`QSerialPortInfo`) se eliminó por completo — confirmado que el iSMC no se conecta por COM/baudios. En su lugar, un campo de IP (`hostAddressInput`) validado con regex IPv4/hostname antes de conectar, precargado con la última IP exitosa (persistida en `local_connection_settings.json`, no versionado) o con el valor de fábrica `192.168.7.1`. El botón "Connect" sigue lanzando `AerotechController.connect()` en el mismo `QThread` (`_ConnectWorker`) de siempre.

### 6.8. `src/ui_extensions_calibration.py`
Amplía lo que ya existía (foco Z, Zero X/Y) con tres piezas nuevas en agosto de 2026:
- **Foco Z**: lectura de `Current Z` en vivo (timer propio de 100 ms) + botón "Confirm focus" (antes `calibratedBtn`, mismo mecanismo `controller.zero_axis(Z)`, ahora con ese texto).
- **Master safety window**: `setCorner1Btn`/`setCorner2Btn` capturan la posición X/Y actual (tras mover con el jog de Manual) como esquinas; `get_safety_window()` expone `{x_min, x_max, y_min, y_max}` a Auto (`_validate_window`) y G-Code (`M901`). Redefinir una esquina ya capturada exige confirmación explícita (`QMessageBox`).
- **Laser alignment mode**: `alignmentModeToggle` fuerza un tope de potencia (`config.ALIGNMENT_MODE_MAX_POWER_PERCENT`) y habilita `alignmentFireBtn`, con el mismo patrón de disparo por mantener-pulsado que Manual (`pso_output_on`/`pso_output_off`). Al desactivar el modo, fuerza `pso_output_off()`.

### 6.9. `src/aerotech_controller.py`
Clase `AerotechController`: envoltorio único sobre el SDK `automation1`, descrito en detalle en el punto 5.5. Es el único módulo que importa `automation1` directamente; el resto de páginas solo llaman a sus métodos. Amplía en agosto de 2026 con `get_axis_indicators(axis)` (sustituye a las antiguas `get_axes_enabled()`/`get_axes_homed()`/`get_axis_faults()`) y toda la capa PSO (`pso_reset`, `pso_configure_fixed_distance`, `pso_configure_array_distances`, `pso_configure_waveform`, `pso_configure_window`, `pso_configure_bitmap`, `pso_output_on`, `pso_output_off`) — ver sección 12.

---

## 7. Estado actual y trabajo pendiente

- **Integración de hardware real**: implementada y con la sintaxis mayormente verificada contra el SDK `automation1` instalado (`Controller.connect/start`, `StatusItemConfiguration`, `motion.moveincremental/moveabsolute/home`, `motion_setup.setupaxisrampvalue`). Sin la estación física conectada, cada operación se prueba en modo "sin conexión" (falla de forma controlada, registrada por consola); falta la validación final con el iSMC real en el laboratorio.
- **Capa PSO sin confirmar** (nueva, sección 12): namespace y nombres de método de `runtime.commands.pso.*` no verificados contra la API real, ni el número de salida PSO físico conectado al NEJE. Ver `# TODO` en `aerotech_controller.py`.
- **Bits de estado sin verificar**: `get_axis_indicators()` (sección 12) asume nombres de bit de `a1.AxisStatus`/`a1.DriveStatus`/`a1.AxisFault` — `in_position` en particular no se ha usado hasta ahora en el proyecto — que no se han contrastado todavía contra la instalación real del SDK.
- **Llamadas bloqueantes en el hilo de la UI**: `home_axes()`, `G4` (dwell, `time.sleep()`) y la ejecución de G-Code síncrona pueden congelar la ventana mientras esperan al controlador. Solo la conexión inicial (`Connect`) se ejecuta ya en un `QThread`.
- **Dialecto G-Code incompleto para Point array irregular y Binary pattern**: `M900`/`M901` cubren distancia fija y ventana PSO, pero no hay todavía un M-code para arrays de distancias no uniformes ni para patrones de bits — Auto los aproxima o los deja como comentario (ver 6.5/6.6 y sección 12).
- **Dual-PSO Adapter (ECZ03125-3)**: cableado ya instalado entre Drive 1 y Drive 2; podría habilitar disparo diagonal real en "Point array", pero no está verificado en laboratorio (`config.SYNC_PORTS_AVAILABLE = False`).
- **Sin control de versiones**: el directorio de trabajo no es (todavía) un repositorio Git.
- **Sin fichero de dependencias**: falta un `requirements.txt`/`pyproject.toml` para fijar versiones y facilitar la reproducibilidad del entorno.
- **Ruta de fuente tipográfica**: `GuiFunctions.loadFont()` (en `main.py`) carga la fuente desde `.fonts/google-sans-cufonfonts/ProductSans-Regular.ttf`, carpeta que no existe actualmente en el proyecto (falla de forma silenciosa y Qt usa una fuente de reemplazo).
- **Interlock del láser**: sigue en gris fijo (`config.LASER_INTERLOCK_AVAILABLE = False`) hasta confirmar la señal en el interconnect real — ya no hay slot de interlock visible en Home (eliminado en la migración de agosto de 2026), pero el flag sigue existiendo por si se usa en otra página en el futuro.

---

## 8. Cómo ejecutar el proyecto

```bash
python main.py
```

Requiere Python 3.12 y las dependencias listadas en la sección 3 instaladas en el entorno (`pip install PySide6 QT-PyQt-PySide-Custom-Widgets qtsass libsass cairosvg watchdog`, como mínimo, para la parte de interfaz/temas). El primer arranque tras cambiar de tema puede tardar unos segundos mientras `Custom_Widgets` genera en segundo plano los iconos coloreados que falten.

---

## 9. Rediseño de la página Home (2026-08-14)

> **Parcialmente superseded por la sección 12** (2026-08-19): el banner de conexión/STO y la matriz de LEDs por eje descritos aquí se migraron a `GlobalStatusPanel` (`main.py`), y `get_axis_faults()`/`get_axes_homed()` se sustituyeron por `get_axis_indicators()`. Se conserva este registro como historial — la tarjeta "Salida Láser" descrita abajo sigue siendo la base de lo que hoy queda en `ui_extensions_home.py`.

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

Ver detalle en las secciones 5.5, 6.9 y 7. Resumen: se añadieron `get_axis_faults()`, `get_axes_homed()`, `get_sto_status(axis=None)`, `set_laser_power_percent(duty_percent)`, `get_laser_output_state()` y la constante `NEJE_B30635_MAX_POWER_MW`, sin eliminar ni modificar el comportamiento de ningún método existente. Se creó `config.py` con el flag `LASER_INTERLOCK_AVAILABLE = False`.

### 9.5. Pendiente / no implementado en esta fase

- Verificar contra la instalación real de `automation1` los nombres de bit usados en `get_axis_faults()`, `get_axes_homed()` y `get_sto_status()` (marcados con `# TODO` en el código).
- Confirmar el canal PWM/TTL físico del láser NEJE B30635 contra el documento *620D1426-10-01 System Interconnect* y conectar `set_laser_power_percent()` a la salida real.
- Confirmar la señal de interlock en el interconnect y activar `config.LASER_INTERLOCK_AVAILABLE`.
- Migración de las páginas Manual/Auto/G-Code del antiguo `set_digital_output` del shutter al nuevo esquema de PWM/láser (fuera de alcance de este cambio).

### 9.6. Ajuste visual posterior: tamaños y tarjeta intermedia de estado por eje

Segunda pasada, solo de maquetación, sobre la misma página Home:

- **Banner** (`statusBanner`): altura mínima/máxima subida de 40-48 px a 64-90 px, márgenes internos de 24×8 px, fuentes de `labelConexion`/`labelSTO` a 13 pt negrita, LEDs de 16→20 px. El grupo conexión+STO ya no queda anclado a los bordes: se centra como bloque en medio del banner (spacers `Expanding` a ambos lados + separador fijo de 60 px entre los dos grupos), en vez del reparto "conexión a la izquierda / STO a la derecha" original.
- **Nueva tarjeta intermedia `axisStatusCard`**, insertada entre `positionStatus` (imagen + X/Y/Z) y `cardsFrame` (tarjeta de láser). Sustituye a las filas de 4 LEDs que antes colgaban debajo de cada eje (`Habilitado`/`Homed`/`Sin error de posición`/`Límites libres`, eliminadas). En su lugar, una matriz (`QGridLayout` `gridLayout_axisStatus`) con:
  - Columnas: **X**, **Y**, **Z**.
  - Filas: **Límite CW**, **Límite CCW**, **Fallo**, **Referenciado** — un LED de 16 px por celda.
  - El indicador "Habilitado" (que dependía de `get_axes_enabled()`, booleano combinado para los 3 ejes sin desglose real por eje) se retiró de la matriz junto con el resto del rediseño; `update_position_display()` ya no llama a `get_axes_enabled()` en absoluto, lo que además resuelve de raíz la limitación apuntada en la sección 9.3 sobre ese valor combinado.
  - Mismo patrón visual que las otras dos tarjetas (icono `activity.png`, título, sombra vía `apply_card_shadow()`, fondo de tarjeta vía el selector SCSS compartido `QFrame#laserOutputCard, #axisStatusCard`).
- **Tarjeta `laserOutputCard`**: ancho máximo subido de 250 a 340 px, icono de 50→64 px, márgenes internos 24×20 px y espaciado 14 px entre elementos, fuentes del título/estado subidas (11→13 pt / 10→12 pt), LEDs de 16→20 px, campo `estadoPotencia` agrandado (200-300×32 px → 260-360×40 px, fuente 9→11 pt).
- **Posición X/Y/Z**: etiquetas de eje a 13 pt negrita (antes 11), valores a 15 pt con ancho mínimo de 110 px (antes 11 pt sin mínimo), más espaciado vertical entre las 3 líneas (`verticalLayout_20.setSpacing(16)`).
- `homePage` pasó de tener `horizontalLayout_18` como único layout (`QHBoxLayout(self.homePage)`) a un `verticalLayout_home` que apila banner + fila horizontal (posición / estado de ejes / láser) — ya introducido en la sección 9.2, ahora con la tarjeta de ejes como tercer elemento de esa fila.

---

## 10. Rediseño de la página Manual (2026-08-14)

> **Parcialmente superseded por la sección 12** (2026-08-19): la copia de posición/LEDs por eje descrita aquí se eliminó (vive en `GlobalStatusPanel`), el control de aceleración desapareció de la interfaz, y el láser pasó de "en vivo" a "mantener pulsado" sobre PSO real — `laserOffBtn` ya no existe, sustituido por `laserFireBtn`. Se conserva este registro como historial.

Cambio de alcance acotado a la página **Manual** (`src/ui_interface.py`, `src/ui_extensions_manual.py`), reutilizando sin modificarlos los métodos que la fase de Home (sección 9) ya había añadido a `src/aerotech_controller.py` (`get_axis_faults()`, `get_axes_homed()`, `get_sto_status()`, `set_laser_power_percent()`, `get_laser_output_state()`, `NEJE_B30635_MAX_POWER_MW`). No se ha tocado Home, Auto, G-Code, Connection ni Calibration.

### 10.1. Cambios de interfaz (`src/ui_interface.py`)

- **Control por eje** (`axisControlManual`, encima de la sección de movimiento XYZ): tres bloques idénticos (`axisControlX/Y/Z`), cada uno con un botón conmutable `toggle<Axis>Btn` (mismo patrón que `connectBtn`: `setCheckable(True)`, cambia de texto/color según estado), un botón `home<Axis>Btn` y una fila `ledRowManual<Axis>` para los 4 LEDs de estado del eje.
- **Posición en vivo** (`positionManual`, junto al D-pad dentro de `widget_8`): tres pares etiqueta/valor (`labelPosManualX/Y/Z` + `valorXManual/YManual/ZManual`), mismo formato que Home.
- **Multiplicador de escala**: `scaleList` se envolvió en un `scaleRow` (`QFrame`+`QHBoxLayout`) junto con el nuevo `scaleMultiplier` (`QSpinBox`, rango 1-999, valor por defecto 1), ocupando la misma celda de `gridLayout_4` que antes ocupaba `scaleList` solo — no se tocó la disposición de `velocity`/`acceleration`.
- **Sección de láser**: `openShutterBtn`/`closeShutterBtn` eliminados. En su lugar, dentro de `frame_7`: `laserPowerRow` (`QFrame`+`QHBoxLayout`) con `laserPowerSlider` (`QSlider` horizontal, 0-100) y `labelLaserPowerManual` (`QLineEdit` de solo lectura), y debajo `laserOffBtn` (tamaño mínimo 150×60 px). `laserOC` se mantiene tal cual (imagen base `images/laserOC4.png`), solo cambia cómo se colorea (ver 10.2).
- Import añadidos: `QSlider`, `QSpinBox` (no estaban en uso en este fichero hasta ahora).

### 10.2. Cambios de lógica (`src/ui_extensions_manual.py`)

- **Reutilización de `_make_led()`/`_set_led_color()` de `HomePageExtensions` sin duplicarlos ni modificar `ui_extensions_home.py`**: ambos métodos no usan ningún atributo de instancia (`self.ui`/`self.controller`), así que `ManualPageExtensions` los invoca pasándose a sí misma como `self` (`HomePageExtensions._make_led(self, ...)`). Es una reutilización deliberada de la implementación exacta, no una copia — si `_make_led()` cambiara alguna vez a depender de `self.ui`, esta llamada dejaría de ser válida y habría que revisarla.
- **Control por eje**: `toggle<Axis>Btn` llama a `controller.enable_axes([AXIS_<X|Y|Z>])`/`disable_axes([...])` según su estado `isChecked()`; `home<Axis>Btn` llama a `controller.home_axes([AXIS_<X|Y|Z>])`. No se ha modificado la firma de estos tres métodos en `aerotech_controller.py` — ya aceptaban una lista de ejes.
- **`update_status_display()`** (nuevo, en un `QTimer` propio de 100 ms, independiente del de Home): misma secuencia que `HomePageExtensions.update_position_display()` — sin conexión, todo a "—"/gris; con conexión, posición + `get_axes_enabled()` + `get_axes_homed()` + `get_axis_faults()`. Nota de implementación (igual que en Home, sección 9.3): `get_axes_enabled()` es un booleano combinado para los 3 ejes, así que el LED "Habilitado" de X/Y/Z muestra ese mismo valor en los tres.
- **Compuerta de confirmación real en Velocity/Acceleration**: `self._applied_velocity`/`self._applied_acceleration` (inicializados a 10.0/100.0) son los únicos valores que usan `_move_relative()` y `move_xy_zero()` — ya no leen `self.ui.velocity.value()`/`self.ui.acceleration.value()` directamente. `velocity.valueChanged`/`acceleration.valueChanged` disparan `_check_pending_changes()`, que aplica un borde naranja (`#FFA726`) al spinbox que difiera de su valor aplicado y cambia el texto de `confirmBtn` a "Aplicar cambios pendientes". `confirm_values()` (mismo nombre que antes, lógica reescrita) copia los valores, quita el borde y muestra el mismo `QMessageBox` que ya existía.
- **Paso de jog = escala × multiplicador**: `get_current_scale()` multiplica la conversión de unidad (nm/μm/mm/cm) por `scaleMultiplier.value()`.
- **Control de potencia del láser en vivo**: `laserPowerSlider.valueChanged` (no solo al soltar) llama a `controller.set_laser_power_percent(value)`, actualiza `labelLaserPowerManual` con `"{duty:.0f}% · {mw:.0f} mW"` (el aviso de "consigna, no medida" queda en el `toolTip` del widget, no repetido en el texto) y recalcula el color de `laserOC` con `_laser_color_for_percent()`, que interpola linealmente de gris (`#808080`, 0%) a rojo saturado (`#F44336`, 100%) sin saltos de dos colores. `laserOffBtn.clicked` simplemente hace `laserPowerSlider.setValue(0)`; el resto de la cadena (controlador + color de `laserOC`) se actualiza sola porque el slider ya dispara `valueChanged`. No pasa por ninguna compuerta de confirmación — es intencionalmente en vivo.
- Eliminados: `handle_shutter_button_click()`, `update_laser_icon_color()` (verde/rojo fijo) y las constantes `SHUTTER_OUTPUT_AXIS`/`SHUTTER_OUTPUT_NUM` (no se usaban desde ningún otro fichero — `ui_extensions_auto.py` tiene su propia copia independiente de esas constantes para su propio shutter, sin cambios).

### 10.3. Pendiente / no implementado en esta fase

- `home_axes()` sigue siendo una llamada bloqueante ejecutada en el hilo de la UI (ya documentado desde antes de esta fase) — no se ha movido a `QThread`.
- Dos `QTimer` de 100 ms corriendo en paralelo (Home + Manual), cada uno pidiendo estado al controlador por su cuenta — funcionalmente correcto y consistente con el patrón actual (cada `XxxPageExtensions` gestiona sus propias señales), pero si más adelante se detecta demasiada carga de refresco con hardware real conectado, se podría centralizar en un único servicio de estado compartido.
- `set_laser_power_percent()` sigue en modo simulado (ver sección 9.4/9.5): el slider de Manual ya llama a esta función en vivo, pero mientras no se confirme el canal PWM/TTL real, no hay salida física.
- No se ha añadido jog continuo (mantener pulsado) — se mantiene solo clic a paso, según lo decidido.

---

## 11. Consolidación de archivos de arranque (2026-08-14)

Cambio puramente organizativo, sin tocar ningún comportamiento: reducir el número de ficheros de nivel superior fusionando los dos que solo contenían lógica de arranque/orquestación (ejecutados una única vez, ya acoplados entre sí) dentro de `main.py`.

### 11.1. Qué se fusionó y por qué

- **`src/Functions.py`** (clase `GuiFunctions`: fuente, tema visual, señales de menú) y **`src/ui_extensions.py`** (clase `UIExtensions`: orquestador de las 6 páginas + instancia compartida de `AerotechController`) se movieron íntegros a `main.py`, debajo de `MainWindow`. Ambos ficheros originales se eliminaron.
- **Qué NO se tocó**: `src/ui_interface.py` (construcción de widgets) y `src/aerotech_controller.py` (envoltorio del SDK) se mantuvieron como ficheros aparte — son las dos piezas con una identidad propia clara (una es boilerplate mecánico de ~2200 líneas, la otra es la única capa sin dependencia de Qt) y mezclarlas con el resto habría diluido una separación que hoy es fácil de explicar en la memoria del TFG. Los 6 `ui_extensions_*.py` (uno por página) tampoco se tocaron.
- **Criterio usado**: solo se fusionaron ficheros que (a) se ejecutan una única vez al arrancar, (b) ya estaban acoplados entre sí (`main.py` los importaba y llamaba a ambos directamente) y (c) eran pequeños (103 y 90 líneas). `ui_interface.py`/`aerotech_controller.py` no cumplían (a) por tamaño/naturaleza distinta, así que se descartó fusionarlos pese a que el usuario lo planteó como alternativa más agresiva.

### 11.2. Resultado

De 12 ficheros de código propio (`main.py`, `config.py`, `src/Functions.py`, `src/ui_extensions.py`, `src/ui_interface.py`, `src/aerotech_controller.py` + 6 `ui_extensions_*.py`) se pasó a **10**: `main.py` (ahora con `MainWindow` + `UIExtensions` + `GuiFunctions`, ~273 líneas, organizado con comentarios de sección), `config.py`, `src/ui_interface.py`, `src/aerotech_controller.py` y los 6 `ui_extensions_*.py`, sin cambios de comportamiento — verificado arrancando la app en modo simulado tras el cambio.

### 11.3. Cómo importar ahora

Cualquier código nuevo que necesitase antes `from src.Functions import GuiFunctions` o `from src.ui_extensions import UIExtensions` ya no debe hacerlo — ambas clases están en el propio `main.py`. Ningún fichero de `src/ui_extensions_*.py` importaba de estos dos módulos (se comprobó antes de eliminarlos), así que no hizo falta tocar ninguna página.

---

## 12. Migración a panel de estado global + generador de G-Code en Auto + capa PSO (2026-08-19)

Migración aplicada en el orden `00_global_architecture.md` → `01_home.md` → `02_manual.md` → `03_auto.md` → `04_gcode.md` → `05_calibration.md` → `06_connection.md`. A diferencia de las fases anteriores (secciones 9-11, solo aditivas), esta es una **migración**: extrae a un panel compartido lo que Home y Manual ya tenían cada uno por su cuenta, sustituye por completo la implementación de Auto, y construye desde cero una capa PSO que no existía. Todo el texto visible nuevo/tocado se redactó en **inglés**, por instrucción explícita del documento `00`.

### 12.1. `GlobalStatusPanel` (`main.py`) — panel de estado compartido

Nuevo `QFrame`, construido una única vez en `MainWindow.__init__` e insertado fuera del `QStackedWidget` principal (`self.ui.verticalLayout_11.insertWidget(0, ...)`, justo encima de `mainPages`). Diseño en dos filas (rediseñado el 2026-08-19 a partir de un mockup del usuario):
- **Fila superior**: LED + texto de conexión (`"Connected — <host>"` / `"Disconnected"`), LED + texto de STO (`"Safety OK"` / `"STO ACTIVE"`, con el fondo del panel entero en rojo de alerta fijo `#DA190B` cuando está activo), y a la derecha el botón **"LASER STOP"** (llama a `controller.pso_output_off(AXIS_X)` y emite la señal `laser_emergency_stop`).
- **Fila inferior**: tres tarjetas, una por eje (`_build_axis_card()`), cada una con la letra del eje + su posición en vivo (`"12.400 mm"`) en la cabecera, y debajo una fila de 4 LEDs sin etiqueta visible (Enabled/Homed/In Position/No limit active — el nombre completo queda en el `toolTip` de cada LED, no como texto en pantalla).

Visible solo en Home/Manual/Auto: `MainWindow._update_global_panel_visibility(index)`, conectado a `mainPages.currentChanged`, oculta el panel en G-Code/Connection/Calibration. Un único `QTimer` de 100 ms, propiedad de `MainWindow` (no del panel), llama a `GlobalStatusPanel.update_status()` — sustituye a los dos `QTimer` independientes que antes corrían en paralelo en `HomePageExtensions` y `ManualPageExtensions` (limitación señalada en las secciones 9.3/10.3, resuelta aquí).

`AerotechController` ahora se crea en `MainWindow.__init__` (no dentro de `UIExtensions`) para poder pasarse tanto a `UIExtensions` como a `GlobalStatusPanel`; `UIExtensions.__init__` cambió de firma (`ui, main_window, controller`) para recibirlo en vez de crearlo.

### 12.2. Home (`ui_interface.py`, `ui_extensions_home.py`) — simplificación drástica

Eliminados de `homePage`/`HomePageExtensions`: `statusBanner` y su lógica, `axisStatusCard` (matriz de LEDs), las etiquetas de posición (`valorX`/`valorY`/`valorZ` + `label_16`/`label_14`/`label_12`), y el slot de interlock (`labelInterlock` + su LED — confirmado que esa señal no existe). Lo que queda, en horizontal: la tarjeta `laserOutputCard` (LED ON/OFF con **borde punteado si `is_measured` es `False`**, texto `estadoPotencia` con formato `"{duty:.0f}% · {mw:.0f} mW (setpoint)"`) y `estacionAerotech`, uno al lado del otro. `update_position_display()` se renombró a `update_laser_card()`. El `QTimer` de 100 ms de Home se eliminó del todo — la tarjeta se refresca con un timer propio mucho más ligero (100 ms, solo lee `get_laser_output_state()`, ya no posición).

### 12.3. Manual (`ui_interface.py`, `ui_extensions_manual.py`) — sin posición/LEDs propios, sin aceleración, láser sobre PSO

- `positionManual`, `labelPosManualX/Y/Z`, `valorXManual/YManual/ZManual` y `ledRowManual<Axis>` eliminados por completo (cubiertos por el panel global). `axisControlManual` (los 3 bloques `toggle<Axis>Btn`/`home<Axis>Btn`) se mantiene — son controles activos, no un indicador pasivo — pero pierde su fila de LEDs.
- El spinbox `acceleration` (y `label_33`) se eliminó de la interfaz; la aceleración pasa a `config.DEFAULT_ACCELERATION_MM_S2[axis]`, fija. Solo `velocity` conserva la compuerta de confirmación (borde naranja + `confirmBtn`).
- `laserPowerSlider` deja de llamar a `controller.set_laser_power_percent()` en `valueChanged` — ahora solo actualiza el texto/color en vivo. `laserOffBtn` se renombró a **`laserFireBtn`** (texto "Laser ON"), y pasó de `clicked` a `pressed`/`released`: mientras se mantiene pulsado, llama a `pso_configure_waveform(AXIS_X, power)` + `pso_output_on(AXIS_X)`; al soltar, `pso_output_off(AXIS_X)`. `handle_emergency_stop()` (nuevo) está conectado a `GlobalStatusPanel.laser_emergency_stop` desde `MainWindow.__init__`.

### 12.4. Auto (`ui_interface.py`, `ui_extensions_auto.py`) — reescritura completa

Eliminados: `moveBtn`, `velocity_2`, `acceleration_2`, `scaleList_2`, `confirmBtn_2` (y su sincronización bidireccional con Manual), `resetBtn`, todo el bloque de *shutter* temporizado (`scaleListTime`, `timeShutter`, `acceptBtn`, `timeGraph`, `_saved_shutter_time_s`). Auto ya no ejecuta movimiento directamente.

Sustituido por un **generador de G-Code de 5 modos** (`modeSelector` + `modeStack`, cada modo con su propio panel de campos, sin formulario genérico compartido):

| Modo | Campos propios |
|---|---|
| Single point | Position X/Y/Z, "Fire at this point", Duration+scale (dispara a 100% fijo — la tabla de campos no incluye un control de potencia para este modo) |
| Fixed-distance firing | Start/End point, Distance+scale, Pulses/event, Power %, Travel speed, Limit to position window |
| Point array | Lista de pasadas (`Add pass`/`Remove pass`, cada una alineada a un único eje X o Y), Spacing (Uniform/Irregular), Distance+scale, Pulses/event, Power %, Travel speed, Limit to position window |
| Power gradient | Gradient type (Linear/Radial, sub-panel propio), Distance+scale, Power start %→end %, Travel speed — **siempre segmentado** (G1 cortos + `M3 S<valor>` escalonado), con el aviso fijo *"Segmented approximation — not a native PSO array."* visible en el panel |
| Binary pattern | Start/End point, Distance+scale, 8 toggles de bit, Travel speed |

Cada modo genera G-Code siempre envuelto en `G28`…`G28`; cualquier cambio de campo regenera la vista previa (`gcodePreviewAuto`) en vivo. "Open in G-Code" llama a `gcode_ext.load_gcode_text()`; "Download file" exporta a `.gcode` vía `QFileDialog`. `fdLimitWindow`/`paLimitWindow` validan contra `calibration_ext.get_safety_window()`. Auto tiene su propia copia de control por eje (`axisControlAuto`), construida de nuevo porque no comparte esos widgets con Manual.

**Huecos honestos, documentados con `# TODO` en el código**: el dialecto G-Code de `04_gcode.md` no define un M-code para arrays de distancias irregulares ni para patrones de bits, así que `Point array` (Irregular) aproxima con `M900` de distancia fija, y `Binary pattern` deja el patrón como comentario (`; binary pattern ...`) en vez de un comando ejecutable.

### 12.5. G-Code (`ui_interface.py`, `ui_extensions_gcode.py`) — vista previa + dialecto ampliado

Sin tocar la distribución existente (drag-and-drop, "Select file", "Edit", "Start"): se añadió un panel de solo lectura (`gcodePreview`, monoespaciado) al lado del drag-and-drop, en la misma fila (`horizontalLayout_gcodeSplit`). Nuevo método público `load_gcode_text(text)`, usado por el botón "Open in G-Code" de Auto. El intérprete amplió `GCODE_SUPPORTED` con `G4 P<ms>` (dwell), `M3 S<0-100>` (PSO on con potencia), `M5` (PSO off), `M900 D<mm> P<pulsos>` (distancia fija PSO — el número de pulsos se guarda en `_pending_pulse_count` y se aplica al `M3` siguiente, porque `pso_configure_fixed_distance()` no acepta ese parámetro) y `M901 X<min> X<max> Y<min> Y<max>` (ventana PSO, parseada aparte porque repite la letra X/Y en la misma línea, y validada contra `calibration_ext.get_safety_window()`).

### 12.6. Calibration (`ui_interface.py`, `ui_extensions_calibration.py`) — aditivo

- **Foco Z**: lectura `Current Z: {z:.3f} mm` en vivo (timer propio de 100 ms). `calibratedBtn` cambió su texto a **"Confirm focus"**; sigue llamando a `controller.zero_axis(AXIS_Z)` (mismo mecanismo de siempre, no se creó una función paralela).
- **Master safety window** (nuevo): `xMinField`/`xMaxField`/`yMinField`/`yMaxField` (solo lectura) + `setCorner1Btn`/`setCorner2Btn`, que capturan `controller.get_axis_positions()` tras mover el eje con el jog de Manual hasta la esquina real. `get_safety_window()` expone `{x_min, x_max, y_min, y_max}` (o `None` si faltan esquinas) a Auto y G-Code. Redefinir una esquina ya capturada exige confirmar en un `QMessageBox`.
- **Laser alignment mode** (nuevo): `alignmentModeToggle` fuerza `config.ALIGNMENT_MODE_MAX_POWER_PERCENT` (8%) y habilita `alignmentFireBtn`, mismo patrón de mantener-pulsado que Manual (`pso_configure_waveform`/`pso_output_on`/`pso_output_off`). Al desactivar el toggle, fuerza `pso_output_off()`.

### 12.7. Connection (`ui_interface.py`, `ui_extensions_connection.py`) — IP en vez de serie

`comPort`/`baudRate` (`QSerialPortInfo`) eliminados por completo. Nuevo `hostAddressInput`, precargado con `controller.host` si ya hubo un intento en la sesión, si no con la última IP guardada en `local_connection_settings.json` (fichero local, no versionado — añadido a `.gitignore`), si no con `192.168.7.1`. `handle_connect_click()` valida el formato (regex IPv4 o hostname RFC 1123 simplificado) antes de lanzar el mismo `QThread`/`_ConnectWorker` de siempre; tras una conexión exitosa con una IP distinta de la de fábrica, se guarda para la próxima vez. No se tocó `_ConnectWorker`, no se añadió reconexión automática, y `AerotechController.connect()` conserva su valor por defecto.

### 12.8. `config.py` — nuevos flags

```python
SYNC_PORTS_AVAILABLE = False        # Dual-PSO Adapter (ECZ03125-3), sin verificar en laboratorio
DEFAULT_ACCELERATION_MM_S2 = {"X": 100.0, "Y": 100.0, "Z": 100.0}
ALIGNMENT_MODE_MAX_POWER_PERCENT = 8
```

### 12.9. Pendiente de hardware, no de diseño

- Nombres exactos de función/enum de PSO en Python para XC2e/iXC2e (`runtime.commands.pso.*` es un namespace probable, no confirmado).
- Número de salida PSO real conectado al NEJE (documento de interconexión 620D1426-10-01).
- Si las distancias del array PSO son relativas o absolutas entre eventos.
- Si el Dual-PSO Adapter permite disparo diagonal real en "Point array".
- Bits exactos de `AxisStatus`/`DriveStatus` para `in_position` (nunca usado antes en el proyecto).

### 12.10. Verificación

`python -m py_compile` sobre todos los ficheros tocados, y arranque completo de la app (`python main.py`) sin excepciones en modo simulado tras cada fase (00 → 06) y al final del conjunto completo.

## 13. Parche visual — panel global, Calibration, Manual (2026-08-28)

Parche de ajustes visuales sobre el resultado de la sección 12 (sin cambios de lógica de negocio salvo donde se indica). Verificado con un arranque offscreen (`QT_QPA_PLATFORM=offscreen`) capturando Manual y Calibration.

- **`GlobalStatusPanel` (`main.py`)**: de 4 LEDs por eje a 3 — `Enabled`/`Homed`/`CW-CCW` (nombres completos, ya no abreviaturas), eliminado el LED `INP`/"in position". Eliminado el bloque de STO por completo (LED, texto, y el tinte rojo del banner en fallo) — no hay señal de STO cableada; `get_sto_status()` sigue existiendo en `aerotech_controller.py` sin usarse desde aquí. Banner de conexión + "Laser stop" ya estaba en una sola fila (`QHBoxLayout`); el ancho del botón "Laser stop" ahora se calcula con `QFontMetrics` sobre el texto real en vez de un `QSize` fijo adivinado.
- **`aerotech_controller.get_axis_indicators()`**: sustituye `in_position`/`no_limit_active` por `limit_active: bool` (true si CW o CCW activo). Diccionario resultante: `{"enabled", "homed", "limit_active"}`.
- **Calibration (`ui_interface.py`, `ui_extensions_calibration.py`)**: `calibrationPage` pasó de `QWidget` a `QScrollArea` (con `calibrationPageContents` como widget interior) — el objectName `"calibrationPage"` se mantuvo en el `QScrollArea` porque la navegación del menú lateral (`json-styles/style.json`) busca ese nombre dentro de `rightMenuPages`. Etiquetas acortadas para que quepan en el ancho del panel lateral: "Set corner 1/2" → "Corner 1/2", "Laser alignment mode" → "Alignment mode". Nuevo helper `_fit_button_width()` (basado en `QFontMetrics`) aplicado a todos los botones de la página (focus Up/Down, Confirm focus, Zero X/Y Position, Corner 1/2, Alignment mode, Fire) en vez de dejar que el ancho lo fije el contenedor padre.
- **Manual — Enable/Home (`ui_interface.py`, `ui_extensions_manual.py`)**: los 3 frames `axisControlX/Y/Z` (cada uno con label + 2 botones apilados) se sustituyeron por un único `QGridLayout` (`gridLayout_axisControl`) de 2 filas — fila de encabezados `X`/`Y`/`Z` centrados, fila de 6 botones (`Ena`/`Home` × 3 ejes) con columnas espaciadoras más anchas entre parejas de eje que dentro de cada pareja. El texto del botón de habilitación pasó de alternar `"ENABLE"`/`"DISABLE"` a un `"Ena"` fijo — el estado enabled/disabled ya lo indica el color vía `QPushButton:checked`.
- **Manual — D-pad XY y Z+/Z-**: revisados; ya usaban `QGridLayout`/`QVBoxLayout` (sin `setGeometry`/coordenadas fijas), así que no hicieron falta cambios — confirmado visualmente en la captura offscreen que el D-pad se ve completo y Z+/Z- no se superponen.

## 14. Parche visual, ronda 2 (2026-08-28)

Segundo parche sobre la sección 13, mismo alcance (visual, sin lógica de negocio salvo donde se indica). Verificado igual que la ronda 1, con un arranque offscreen y capturas de Home/Manual/Auto/Calibration.

- **"Laser stop" (`main.py`)**: el cálculo dinámico de ancho vía `QFontMetrics` (ronda 1) seguía sin ser suficiente — sustituido por `setMinimumWidth(180)` fijo y generoso, repetido como `min-width` en el QSS de instancia, sin stretch factor en `top_row` que pudiera comprimirlo.
- **Arranque en Manual en vez de Home**: causa raíz en `ui_interface.py` — `setupUi()` termina con `self.mainPages.setCurrentIndex(1)` (índice de `manualPage`, heredado del Designer). Corregido en `MainWindow.__init__` (`main.py`) con `self.ui.mainPages.setCurrentWidget(self.ui.homePage)` + `self.ui.homeBtn.setChecked(True)`, sin tocar el orden de `addWidget()`. Nota de implementación: `mainPages` es un `QCustomQStackedWidget` (Custom_Widgets) cuyo `setCurrentWidget()` está sobrescrito para animar la transición (`slideToWidget`, ~500 ms) — el índice no cambia de forma síncrona, se resuelve al terminar la animación (confirmado con `wait_ms(800)` en el smoke test offscreen).
- **Manual (`ui_interface.py`, `ui_extensions_manual.py`)**:
  - Los 6 botones de eje pasan de `"Ena"` a `"Enable"` (mismo patrón estático, color vía `:checked`).
  - `verticalLayout_22.setSpacing(6)` (antes heredaba el spacing por defecto del estilo, ~11px) para subir la fila Scale/Velocity y dar más aire al D-pad.
  - `manualPage` pasó de `QWidget` a `QScrollArea` (mismo patrón que `calibrationPage`, con `manualPageContents` como widget interior y el objectName `"manualPage"` conservado en el `QScrollArea` por la navegación de `json-styles/style.json`).
  - `laserOC` se movió de estar al principio de la columna del láser a vivir dentro de `frame_7`, entre `laserBoardPowerBtn` y `laserPowerRow` (orden final: Laser board power → icono centrado → slider → Laser ON).
- **Auto (`ui_interface.py`, `ui_extensions_auto.py`)**: mismo patrón de fila única que Manual — `axisControlAutoX/Y/Z` (3 frames apilados) sustituidos por `gridLayout_axisControlAuto` (encabezados X/Y/Z + fila de 6 botones agrupados de dos en dos). Texto de habilitación también pasa a `"Enable"` estático, igual que Manual.
- **Calibration (`ui_extensions_calibration.py`)**:
  - Nuevo helper `_enable_button_wrap()` (QLabel interno con `wordWrap`, ya que `QPushButton` no lo soporta nativamente) aplicado a los botones de subir/bajar foco, confirmar enfoque y Zero X/Y — sustituye al `_fit_button_width()` de la ronda 1 para estos 5 (forzar el ancho de la frase completa en una sola línea desbordaba el panel lateral). Los métodos de feedback visual (`confirm_focus`, `handle_zero_x`, `handle_zero_y`) ahora actualizan el `QLabel` interno guardado (`_calibratedBtn_label`, `_zeroXBtn_label`, `_zeroYBtn_label`), no el texto del propio `QPushButton` (que quedó vacío).
  - `_fit_button_width()` baja su padding por defecto de 40 a 24 (Corner 1/Corner 2/Alignment mode/Fire, que sí se quedan con ancho de una sola línea) — el padding anterior sumado en pareja excedía el ancho del panel.
  - `label_safetyWindowTitle`, `label_23` y `label_24` pasan a `setWordWrap(True)` — "Master Safety Window" se recortaba por el borde derecho en vez de ajustar línea, y era la causa principal del scroll horizontal de toda la página.
- **`calibrationPage`/`manualPage` (`ui_interface.py`)**: `setFrameShape(QFrame.NoFrame)` no bastaba para que el `QScrollArea` se viera como una sola caja — su viewport interno seguía pintando un fondo propio. Añadido `setStyleSheet("QScrollArea { background: transparent; border: none; }")` en el propio `QScrollArea` y `viewport().setStyleSheet("background: transparent;")` en su viewport, en ambas páginas.
