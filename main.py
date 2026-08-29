########################################################################
## INTERFAZ GUI ESTACIÓN LÁSER
########################################################################

import sys

import config

# Importar el archivo GUI
from src.ui_interface import *

# Importar Custom widgets
from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings

from PySide6.QtCore import QSettings, QTimer, Signal
from PySide6.QtGui import QFont, QFontDatabase

# Gestor centralizado de la conexión con el controlador Aerotech Automation1-iSMC
from src.aerotech_controller import AerotechController

# Extensiones de cada página
from src.ui_extensions_home import HomePageExtensions
from src.ui_extensions_manual import ManualPageExtensions
from src.ui_extensions_auto import AutoPageExtensions
from src.ui_extensions_gcode import GCodePageExtensions
from src.ui_extensions_connection import ConnectionPageExtensions
from src.ui_extensions_calibration import CalibrationPageExtensions


########################################################################
## GLOBAL STATUS PANEL
## Panel de estado compartido por Home/Manual/Auto: banner de conexión y el
## botón de parada de emergencia del láser en una sola fila, posición X/Y/Z
## en vivo y matriz de LEDs por eje (Enabled/Homed/CW-CCW). Construido una
## vez aquí, fuera del QStackedWidget principal — sustituye a los paneles
## duplicados que Home y Manual tenían cada uno por su cuenta antes de esta
## migración (ver PROGRESO.md, sección de agosto de 2026).
##
## No hay señal de STO cableada en la instalación — el panel no muestra ni
## lee estado de STO (get_sto_status() sigue existiendo en
## aerotech_controller.py, pero este panel ya no lo llama).
########################################################################
class GlobalStatusPanel(QFrame):

    laser_emergency_stop = Signal()

    LED_COLOR_OK = "#4CAF50"
    LED_COLOR_INACTIVE = "#808080"
    LED_COLOR_FAULT = "#F44336"

    AXIS_ORDER = ("X", "Y", "Z")
    # (clave interna en get_axis_indicators(), etiqueta visible bajo el LED, tooltip)
    INDICATORS = [
        ("enabled", "Enabled", "Enabled"),
        ("homed", "Homed", "Homed"),
        ("limit_active", "CW/CCW", "CW or CCW travel limit active"),
    ]

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setObjectName(u"globalStatusPanel")
        self._axis_leds = {axis: {} for axis in self.AXIS_ORDER}
        self._axis_position_labels = {}
        self._led_conexion = None
        self._build_ui()

    # ── LED reutilizable (patrón ya usado en el resto del proyecto) ────
    def _make_led(self, color=None, size=16, tooltip=""):
        led = QFrame()
        led.setObjectName(u"globalLed")
        led.setFixedSize(size, size)
        if tooltip:
            led.setToolTip(tooltip)
        self._set_led_color(led, color or self.LED_COLOR_INACTIVE)
        return led

    def _set_led_color(self, led, color):
        size = led.width()
        led.setStyleSheet(
            f"QFrame#globalLed {{ background-color: {color}; border-radius: {size // 2}px; }}"
        )

    # ── Construcción de la interfaz ─────────────────────────────────────
    def _build_ui(self):
        self.setMinimumHeight(170)
        self.setMaximumHeight(230)
        self.setFrameShape(QFrame.StyledPanel)
        # Mismo fondo que las tarjetas (COLOR_BACKGROUND_1, no BACKGROUND_2)
        # para que el hueco entre tarjetas no se note como un tono distinto
        # — todo el banner se lee como un único panel continuo.
        self.setStyleSheet(
            f"QFrame#globalStatusPanel {{ background-color: {config.THEME.COLOR_BACKGROUND_1}; border-radius: 12px; }}"
        )

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(20, 14, 20, 14)
        outer_layout.setSpacing(16)

        # ── Fila superior: conexión + Laser Stop, en una sola fila ───────
        # Ambos contenedores comparten el mismo fondo que las tarjetas de eje
        # (COLOR_BACKGROUND_1) para que el banner se vea como un solo
        # conjunto — "Laser stop" mantiene su relleno rojo (alerta
        # intencional), solo se unifica el fondo del contenedor a su
        # alrededor, no el botón en sí.
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        connection_card = QFrame()
        connection_card.setObjectName(u"connectionCard")
        connection_card.setStyleSheet(f"""
            QFrame#connectionCard {{
                background-color: {config.THEME.COLOR_BACKGROUND_1};
                border-radius: 10px;
            }}
        """)
        connection_layout = QHBoxLayout(connection_card)
        connection_layout.setContentsMargins(14, 10, 14, 10)
        connection_layout.setSpacing(10)

        self._led_conexion = self._make_led(tooltip="Connection status with the iSMC")
        self.label_connection = QLabel("Disconnected")
        self.label_connection.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.label_connection.setStyleSheet(f"color: {config.THEME.COLOR_TEXT_1};")
        connection_layout.addWidget(self._led_conexion)
        connection_layout.addWidget(self.label_connection)
        top_row.addWidget(connection_card)

        top_row.addStretch(1)

        laser_stop_card = QFrame()
        laser_stop_card.setObjectName(u"laserStopCard")
        laser_stop_card.setStyleSheet(f"""
            QFrame#laserStopCard {{
                background-color: {config.THEME.COLOR_BACKGROUND_1};
                border-radius: 10px;
            }}
        """)
        laser_stop_layout = QHBoxLayout(laser_stop_card)
        laser_stop_layout.setContentsMargins(10, 8, 10, 8)

        # Laser stop — corta la salida PSO y avisa a las páginas suscritas.
        # Ancho mínimo fijo y generoso (el cálculo dinámico vía QFontMetrics
        # no fue suficiente — seguía leyéndose recortado). setMinimumWidth
        # explícito en el propio botón, sin stretch factor en top_row que
        # pueda comprimirlo, y min-width repetido en el QSS de instancia
        # para que ninguna regla de QSS global con mayor prioridad de
        # cascada lo reduzca por debajo de este mínimo.
        self.laser_stop_btn = QPushButton("Laser stop")
        self.laser_stop_btn.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.laser_stop_btn.setMinimumWidth(180)
        self.laser_stop_btn.setMinimumHeight(48)
        self.laser_stop_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.laser_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: 2px solid #DA190B;
                border-radius: 8px;
                padding: 8px 18px;
                min-width: 180px;
                min-height: 48px;
            }
            QPushButton:hover { background-color: #DA190B; }
            QPushButton:pressed { background-color: #B71C1C; }
        """)
        self.laser_stop_btn.clicked.connect(self._handle_laser_stop)
        laser_stop_layout.addWidget(self.laser_stop_btn)
        top_row.addWidget(laser_stop_card, 0)

        outer_layout.addLayout(top_row)

        # ── Fila inferior: una tarjeta por eje (posición + LEDs) ─────────
        axes_row = QHBoxLayout()
        axes_row.setSpacing(14)
        for axis in self.AXIS_ORDER:
            axes_row.addWidget(self._build_axis_card(axis), 1)
        outer_layout.addLayout(axes_row)

    def _build_axis_card(self, axis):
        card = QFrame()
        card.setObjectName(f"axisCard_{axis}")
        card.setMinimumHeight(110)
        card.setStyleSheet(f"""
            QFrame#axisCard_{axis} {{
                background-color: {config.THEME.COLOR_BACKGROUND_1};
                border: none;
                border-radius: 10px;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        # Antes 14 — la fila de LEDs quedaba recortada por el borde inferior
        # de la tarjeta con ese espaciado, dentro de la altura fija de la
        # tarjeta (setMinimumHeight(110) más abajo).
        card_layout.setSpacing(4)

        header_row = QHBoxLayout()
        axis_label = QLabel(axis)
        axis_label.setFont(QFont("Sitka Small", 12, QFont.Weight.Bold))
        axis_label.setStyleSheet(f"color: {config.THEME.COLOR_TEXT_1};")
        axis_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        value_label = QLabel("—")
        value_label.setFont(QFont("Sitka Small", 12))
        value_label.setStyleSheet(f"color: {config.THEME.COLOR_TEXT_1};")
        value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_row.addWidget(axis_label)
        header_row.addStretch(1)
        header_row.addWidget(value_label)
        card_layout.addLayout(header_row)
        self._axis_position_labels[axis] = value_label

        led_row = QHBoxLayout()
        led_row.setSpacing(14)
        for key, abbr, tooltip in self.INDICATORS:
            led_row.addLayout(self._build_indicator_row(axis, key, abbr, tooltip))
        led_row.addStretch(1)
        card_layout.addLayout(led_row)

        return card

    def _build_indicator_row(self, axis, key, label_text, tooltip):
        """LED junto a su nombre (Enabled/Homed/CW-CCW) en la misma línea, en
        vez de debajo — diagnóstico (_diag_led_labels.py) confirmó que el
        texto sí se asignaba, con tamaño y posición correctos, incluso
        cuando no se leía en pantalla; layout en fila en vez de columna para
        no depender de que una fila vertical estrecha dejara el texto pegado
        al borde inferior de la tarjeta."""
        row = QHBoxLayout()
        row.setSpacing(5)

        led = self._make_led(size=12, tooltip=f"{tooltip} — axis {axis}")
        self._axis_leds[axis][key] = led
        row.addWidget(led, 0, Qt.AlignVCenter)

        text_label = QLabel(label_text)
        text_label.setFont(QFont("Sitka Small", 8))
        text_label.setStyleSheet("color: #06112B;")
        text_label.setAlignment(Qt.AlignVCenter)
        row.addWidget(text_label, 0, Qt.AlignVCenter)

        return row

    def _handle_laser_stop(self):
        self.controller.stop_laser(cut_power=True)
        self.laser_emergency_stop.emit()

    # ── Refresco periódico (QTimer de 100 ms, propiedad de MainWindow) ──
    def update_status(self):
        if not self.controller.is_connected:
            self._show_disconnected()
            return

        x, y, z = self.controller.get_axis_positions()
        self._axis_position_labels["X"].setText(f"{x:.3f} mm")
        self._axis_position_labels["Y"].setText(f"{y:.3f} mm")
        self._axis_position_labels["Z"].setText(f"{z:.3f} mm")

        self._set_led_color(self._led_conexion, self.LED_COLOR_OK)
        self.label_connection.setText(f"Connected — {self.controller.host}")

        for axis in self.AXIS_ORDER:
            indicators = self.controller.get_axis_indicators(axis)
            leds = self._axis_leds[axis]
            self._set_led_color(leds["enabled"], self.LED_COLOR_OK if indicators["enabled"] else self.LED_COLOR_INACTIVE)
            self._set_led_color(leds["homed"], self.LED_COLOR_OK if indicators["homed"] else self.LED_COLOR_INACTIVE)
            self._set_led_color(
                leds["limit_active"],
                self.LED_COLOR_FAULT if indicators["limit_active"] else self.LED_COLOR_OK,
            )

    def _show_disconnected(self):
        for axis in self.AXIS_ORDER:
            self._axis_position_labels[axis].setText("—")
        self._set_led_color(self._led_conexion, self.LED_COLOR_FAULT)
        self.label_connection.setText("Disconnected")
        for axis in self.AXIS_ORDER:
            for led in self._axis_leds[axis].values():
                self._set_led_color(led, self.LED_COLOR_INACTIVE)


########################################################################
## MAIN WINDOW CLASS
########################################################################
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Especifica la direccion/nombre del archivo json
        loadJsonStyle(self, self.ui, jsonFiles = {
            "json-styles/style.json"
        })

        # Única instancia del controlador Aerotech, compartida por
        # UIExtensions (páginas) y por el GlobalStatusPanel
        self.controller = AerotechController()

        # Panel de estado global — construido fuera del QStackedWidget
        # principal, insertado justo encima de él
        self.global_status_panel = GlobalStatusPanel(self.controller, self)
        self.ui.verticalLayout_11.insertWidget(0, self.global_status_panel)
        self.ui.mainPages.currentChanged.connect(self._update_global_panel_visibility)

        # Aplicar modificaciones de ui_extensions
        self.ui_ext = UIExtensions(self.ui, self, self.controller)
        self.ui_ext.apply_all_modifications()

        # Conectar todas las señales
        self.ui_ext.connect_all_signals()

        # El botón "Laser stop" del panel global corta el disparo en curso
        # en Manual (ver ManualPageExtensions.handle_emergency_stop)
        self.global_status_panel.laser_emergency_stop.connect(
            self.ui_ext.manual_ext.handle_emergency_stop
        )

        # Visibilidad inicial del panel según la página activa al arrancar
        self._update_global_panel_visibility(self.ui.mainPages.currentIndex())

        # Único QTimer de 100 ms, propiedad de MainWindow, que refresca el
        # panel de estado global — sustituye a los dos QTimer independientes
        # que antes corrían en paralelo en Home y Manual
        self.global_status_timer = QTimer(self)
        self.global_status_timer.timeout.connect(self.global_status_panel.update_status)
        self.global_status_timer.start(100)

        # La conexión con el controlador Aerotech Automation1-iSMC se
        # gestiona de forma centralizada en UIExtensions (más abajo en este
        # mismo archivo, y en src/aerotech_controller.py), ya invocada
        # dentro de self.ui_ext.apply_all_modifications() más arriba.

        # setupUi() deja mainPages en el índice 1 (manualPage añadido justo
        # después de homePage en ui_interface.py) — se fuerza aquí a Home,
        # y se sincroniza homeBtn en el menú lateral para que no quede
        # manualBtn marcado como activo mientras se ve Home.
        self.ui.mainPages.setCurrentWidget(self.ui.homePage)
        self.ui.homeBtn.setChecked(True)

        # Muestra la ventana principal
        self.show()

        # Actualiza configuración de la app
        QAppSettings.updateAppSettings(self)

        # Aplica funciones y eventos
        self.app_functions = GuiFunctions(self)

    def _update_global_panel_visibility(self, index):
        """El panel global solo es útil en Home/Manual/Auto — el resto de
        páginas (G-Code, Connection, Calibration) no lo necesitan."""
        current_widget = self.ui.mainPages.widget(index)
        visible_pages = (self.ui.homePage, self.ui.manualPage, self.ui.autoPage)
        self.global_status_panel.setVisible(current_widget in visible_pages)


########################################################################
## UI EXTENSIONS - MAIN CONTROLLER
## Controla y aplica todas las modificaciones de diseño mediante código
########################################################################
class UIExtensions:
    """Clase principal que coordina todas las extensiones de UI"""

    def __init__(self, ui, main_window, controller):
        """
        Inicializa el controlador de extensiones

        Args:
            ui: La interfaz de usuario (Ui_MainWindow)
            main_window: La ventana principal (MainWindow)
            controller: instancia compartida de AerotechController, creada
                en MainWindow.__init__ (compartida también con
                GlobalStatusPanel, no se crea aquí)
        """
        self.ui = ui
        self.main = main_window
        self.controller = controller

        # Inicializar las extensiones de cada página
        self.home_ext = HomePageExtensions(ui, main_window, self.controller)
        self.manual_ext = ManualPageExtensions(ui, main_window, self.controller)
        self.auto_ext = AutoPageExtensions(ui, main_window, self.controller)
        self.gcode_ext = GCodePageExtensions(ui, main_window, self.controller)
        self.connection_ext = ConnectionPageExtensions(ui, main_window, self.controller)
        self.calibration_ext = CalibrationPageExtensions(ui, main_window, self.controller)

    def apply_all_modifications(self):
        """Aplica todas las modificaciones de diseño"""
        # Aplicar fuentes globales
        self.apply_global_fonts()

        # NOTA: la conexión con el iSMC NO se intenta aquí. Controller.connect()
        # es una llamada bloqueante que, si no hay hardware escuchando en el
        # host indicado, puede colgar la interfaz durante mucho tiempo (se ha
        # comprobado que supera el minuto). Por eso la conexión se dispara solo
        # bajo demanda, en un hilo aparte, desde el botón "Connect" de la
        # página de conexión (ver ConnectionPageExtensions).

        # Aplicar modificaciones específicas de cada página
        self.home_ext.apply_modifications()
        self.manual_ext.apply_modifications()
        self.auto_ext.apply_modifications()
        self.gcode_ext.apply_modifications()
        self.connection_ext.apply_modifications()
        self.calibration_ext.apply_modifications()

    def connect_all_signals(self):
        """Conecta todas las señales de cada página"""
        self.home_ext.connect_signals()
        self.manual_ext.connect_signals()
        self.auto_ext.connect_signals()
        self.gcode_ext.connect_signals()
        self.connection_ext.connect_signals()
        self.calibration_ext.connect_signals()

    def apply_global_fonts(self):
        """Aplica las fuentes globales a toda la aplicación"""
        # Fuente base: Sitka Small 10pt
        base_font = QFont("Sitka Small", 10)
        self.main.setFont(base_font)

        # Fuente para títulos: Sitka Small 11pt Bold
        title_font = QFont("Sitka Small", 11)
        title_font.setBold(True)

        # Aplicar fuente de título a los labels principales
        title_labels = [
            self.ui.label_3,   # Settings
            self.ui.label_4,   # Help
            self.ui.label_11,  # Connection Page
            self.ui.label_10,  # Calibration Page
            self.ui.label_19,  # Movement XYZ (Manual)
            self.ui.label_7,   # Laser (Manual)
            self.ui.label_9,   # Upload G-Code
        ]

        for label in title_labels:
            if label:
                label.setFont(title_font)


########################################################################
## FUNCIONES DE LA GUI
## Fuente, tema visual y señales de los botones de menú
########################################################################
class GuiFunctions():
    def __init__(self, MainWindow):
        # Almacena la instancia de la ventana principal
        self.main = MainWindow
        # Almacena la instancia de la ui
        self.ui = MainWindow.ui

        # Aplicar fuente
        self.loadFont()
        # Iniciar app theme
        self.initilizeAppTheme()
        # Conectar los botones de los menus
        self.connectMenuButtons()


    # APLICAR LAS FUNCIONES A LOS BOTONES DEL MENU
    def connectMenuButtons(self):
        """Conectar los botones para expandir/cerrar del menu"""
        # Expandir el menu central
        self.ui.settingsBtn.clicked.connect(lambda:self.ui.centerMenu.expandMenu())
        self.ui.helpBtn.clicked.connect(lambda:self.ui.centerMenu.expandMenu())

        # Cerrar el menu central
        self.ui.closeCenterMenuBtn.clicked.connect(lambda:self.ui.centerMenu.collapseMenu())

        # Expandir el menu derecho
        self.ui.connectionBtn.clicked.connect(lambda:self.ui.rightMenu.expandMenu())
        self.ui.calibrationBtn.clicked.connect(lambda:self.ui.rightMenu.expandMenu())

        # Cerrar el menu derecho
        self.ui.closeRightMenuBtn.clicked.connect(lambda:self.ui.rightMenu.collapseMenu())


    # APLICAR LOS TEMAS (COLORES) A LA UI
    def initilizeAppTheme(self):
        """Configurar el tema de aplicacion"""
        settings = QSettings()
        current_theme = settings.value("THEME")
        # print("Current theme is: ", current_theme)

        # Lista de temas (colores)
        self.populateThemeList(current_theme)

        # Conectar la señal de cambio de tema al cambio de tema de la app
        self.ui.themeList.currentTextChanged.connect(self.changeAppTheme)

    def populateThemeList(self, current_theme):
        """Rellenar la lista con los temas disponibles"""

        # Limpiar la lista antes de llenarla
        self.ui.themeList.clear()

        added_themes = set()  # Para controlar duplicados
        theme_count = 0
        selected_index = 0

        for theme in self.ui.themes:
            # Saltar temas duplicados
            if theme.name in added_themes:
                continue

            # Saltar temas Dark y Light (opcional)
            if theme.name in ['DARK', 'LIGHT']:
                continue

            self.ui.themeList.addItem(theme.name, theme.name)
            added_themes.add(theme.name)

            # Chequear el tema por defecto/tema actual
            if theme.defaultTheme or theme.name == current_theme:
                selected_index = theme_count

            theme_count += 1

        # Seleccionar el tema correcto
        self.ui.themeList.setCurrentIndex(selected_index)

    # APLICAR LA FUENTE DE LETRA
    def loadFont(self):
        """Cargar y aplicar la fuente"""
        font_id = QFontDatabase.addApplicationFont(".fonts/google-sans-cufonfonts/ProductSans-Regular.ttf")
        if font_id == -1:                                                   # Si ya tiene esa letra
            print("Font is already used")
            return

        font_family = QFontDatabase.addApplicationFont(font_id)
        if font_family:
            chosen_font = QFont(font_family[0])
        else:
            chosen_font = QFont("Sans Serif")

        # Aplicar a la pagina principal
        self.main.setFont(chosen_font)


    # Cambiar el tema (color)
    def changeAppTheme(self):
        """Cambiar el tema segun la seleccion"""
        settings = QSettings()
        selected_theme = self.ui.themeList.currentData()
        current_theme = settings.value("THEME")

        if current_theme != selected_theme:
            settings.setValue("THEME", selected_theme)                      # Aplicar el tema nuevo
            QAppSettings.updateAppSettings(self.main, reloadJson=True)


########################################################################
## EXECUTE APP
########################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
########################################################################
## END
########################################################################
