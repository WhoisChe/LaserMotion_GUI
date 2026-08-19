########################################################################
## INTERFAZ GUI ESTACIÓN LÁSER
########################################################################

import sys

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
## Panel de estado compartido por Home/Manual/Auto: banner de conexión/STO,
## posición X/Y/Z en vivo, matriz de LEDs por eje (ENA/HMD/INP/LIM) y el
## botón de parada de emergencia del láser. Construido una vez aquí, fuera
## del QStackedWidget principal — sustituye a los paneles duplicados que
## Home y Manual tenían cada uno por su cuenta antes de esta migración (ver
## PROGRESO.md, sección de agosto de 2026).
########################################################################
class GlobalStatusPanel(QFrame):

    laser_emergency_stop = Signal()

    LED_COLOR_OK = "#4CAF50"
    LED_COLOR_INACTIVE = "#808080"
    LED_COLOR_FAULT = "#F44336"
    BANNER_ALERT_COLOR = "#DA190B"

    AXIS_ORDER = ("X", "Y", "Z")
    # (clave interna en get_axis_indicators(), abreviatura visible bajo el LED, tooltip)
    INDICATORS = [
        ("enabled", "ENA", "Enabled"),
        ("homed", "HMD", "Homed"),
        ("in_position", "INP", "In Position"),
        ("no_limit_active", "LIM", "No limit active"),
    ]

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setObjectName(u"globalStatusPanel")
        self._axis_leds = {axis: {} for axis in self.AXIS_ORDER}
        self._axis_position_labels = {}
        self._led_conexion = None
        self._led_sto = None
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
        self.setStyleSheet(
            "QFrame#globalStatusPanel { background-color: THEME.COLOR_BACKGROUND_2; border-radius: 12px; }"
        )

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(20, 14, 20, 14)
        outer_layout.setSpacing(16)

        # ── Fila superior: conexión + STO + Laser Stop ──────────────────
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self._led_conexion = self._make_led(tooltip="Connection status with the iSMC")
        self.label_connection = QLabel("Disconnected")
        self.label_connection.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.label_connection.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        top_row.addWidget(self._led_conexion)
        top_row.addWidget(self.label_connection)

        top_row.addSpacing(16)

        self._led_sto = self._make_led(tooltip="Safe Torque Off status")
        self.label_sto = QLabel("Safety OK")
        self.label_sto.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.label_sto.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        top_row.addWidget(self._led_sto)
        top_row.addWidget(self.label_sto)

        top_row.addStretch(1)

        # Laser stop — corta la salida PSO y avisa a las páginas suscritas.
        # Tamaño fijo (no solo mínimo) para que el layout nunca lo comprima
        # por debajo de lo necesario para leer el texto completo.
        self.laser_stop_btn = QPushButton("LASER STOP")
        self.laser_stop_btn.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.laser_stop_btn.setMinimumSize(QSize(260, 48))
        self.laser_stop_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.laser_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: 2px solid #DA190B;
                border-radius: 8px;
                padding: 8px 18px;
            }
            QPushButton:hover { background-color: #DA190B; }
            QPushButton:pressed { background-color: #B71C1C; }
        """)
        self.laser_stop_btn.clicked.connect(self._handle_laser_stop)
        top_row.addWidget(self.laser_stop_btn)

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
                background-color: THEME.COLOR_BACKGROUND_1;
                border: 1px solid THEME.COLOR_ACCENT_3;
                border-radius: 10px;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(14)

        header_row = QHBoxLayout()
        axis_label = QLabel(axis)
        axis_label.setFont(QFont("Sitka Small", 12, QFont.Weight.Bold))
        axis_label.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        axis_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        value_label = QLabel("—")
        value_label.setFont(QFont("Sitka Small", 12))
        value_label.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_row.addWidget(axis_label)
        header_row.addStretch(1)
        header_row.addWidget(value_label)
        card_layout.addLayout(header_row)
        self._axis_position_labels[axis] = value_label

        led_row = QHBoxLayout()
        led_row.setSpacing(10)
        for key, abbr, tooltip in self.INDICATORS:
            led_row.addLayout(self._build_indicator_column(axis, key, abbr, tooltip))
        led_row.addStretch(1)
        card_layout.addLayout(led_row)

        return card

    def _build_indicator_column(self, axis, key, abbr, tooltip):
        """LED + su abreviatura debajo (ENA/HMD/INP/LIM), para que se sepa
        qué significa cada uno sin depender solo del toolTip."""
        column = QVBoxLayout()
        column.setSpacing(2)

        led = self._make_led(size=12, tooltip=f"{tooltip} — axis {axis}")
        self._axis_leds[axis][key] = led
        column.addWidget(led, 0, Qt.AlignHCenter)

        abbr_label = QLabel(abbr)
        abbr_label.setFont(QFont("Sitka Small", 7))
        abbr_label.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        abbr_label.setAlignment(Qt.AlignCenter)
        column.addWidget(abbr_label)

        return column

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

        self._update_sto(self.controller.get_sto_status())

        for axis in self.AXIS_ORDER:
            indicators = self.controller.get_axis_indicators(axis)
            leds = self._axis_leds[axis]
            self._set_led_color(leds["enabled"], self.LED_COLOR_OK if indicators["enabled"] else self.LED_COLOR_INACTIVE)
            self._set_led_color(leds["homed"], self.LED_COLOR_OK if indicators["homed"] else self.LED_COLOR_INACTIVE)
            self._set_led_color(leds["in_position"], self.LED_COLOR_OK if indicators["in_position"] else self.LED_COLOR_INACTIVE)
            self._set_led_color(
                leds["no_limit_active"],
                self.LED_COLOR_OK if indicators["no_limit_active"] else self.LED_COLOR_FAULT,
            )

    def _show_disconnected(self):
        for axis in self.AXIS_ORDER:
            self._axis_position_labels[axis].setText("—")
        self._set_led_color(self._led_conexion, self.LED_COLOR_FAULT)
        self.label_connection.setText("Disconnected")
        self._update_sto(False)
        for axis in self.AXIS_ORDER:
            for led in self._axis_leds[axis].values():
                self._set_led_color(led, self.LED_COLOR_INACTIVE)

    def _update_sto(self, sto_active):
        if sto_active:
            self.setStyleSheet(
                f"QFrame#globalStatusPanel {{ background-color: {self.BANNER_ALERT_COLOR}; border-radius: 12px; }}"
            )
            self.label_sto.setText("STO ACTIVE")
        else:
            self.setStyleSheet(
                "QFrame#globalStatusPanel { background-color: THEME.COLOR_BACKGROUND_2; border-radius: 12px; }"
            )
            self.label_sto.setText("Safety OK")
        self._set_led_color(self._led_sto, self.LED_COLOR_FAULT if sto_active else self.LED_COLOR_OK)


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
