########################################################################
## UI EXTENSIONS - MAIN CONTROLLER
## Controla y aplica todas las modificaciones de diseño mediante código
########################################################################

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy

# Importar módulos específicos de cada página
from src.ui_extensions_home import HomePageExtensions
from src.ui_extensions_manual import ManualPageExtensions
from src.ui_extensions_auto import AutoPageExtensions
from src.ui_extensions_gcode import GCodePageExtensions
from src.ui_extensions_connection import ConnectionPageExtensions
from src.ui_extensions_calibration import CalibrationPageExtensions

# Gestor centralizado de la conexión con el controlador Aerotech Automation1-iSMC
from src.aerotech_controller import AerotechController


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
