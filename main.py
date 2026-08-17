########################################################################
## INTERFAZ GUI ESTACIÓN LÁSER
########################################################################

import sys

# Importar el archivo GUI
from src.ui_interface import *

# Importar Custom widgets
from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings

from PySide6.QtCore import QSettings
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

        # Aplicar modificaciones de ui_extensions
        self.ui_ext = UIExtensions(self.ui, self)
        self.ui_ext.apply_all_modifications()

        # Conectar todas las señales
        self.ui_ext.connect_all_signals()

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


########################################################################
## UI EXTENSIONS - MAIN CONTROLLER
## Controla y aplica todas las modificaciones de diseño mediante código
########################################################################
class UIExtensions:
    """Clase principal que coordina todas las extensiones de UI"""

    def __init__(self, ui, main_window):
        """
        Inicializa el controlador de extensiones

        Args:
            ui: La interfaz de usuario (Ui_MainWindow)
            main_window: La ventana principal (MainWindow)
        """
        self.ui = ui
        self.main = main_window

        # Única instancia del controlador Aerotech, compartida por todas
        # las páginas que necesitan mover ejes o leer su estado
        self.controller = AerotechController()

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
            self.ui.label_7,   # Shutter (Manual)
            self.ui.label_15,  # Movement XYZ (Auto)
            self.ui.label_27,  # Shutter (Auto)
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
