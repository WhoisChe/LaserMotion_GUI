########################################################################
## CALIBRATION PAGE EXTENSIONS
## Modificaciones de diseño para la página de calibración
########################################################################

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy

from src.aerotech_controller import AXIS_X, AXIS_Y, AXIS_Z

# Paso, velocidad y aceleración usados para el ajuste fino de enfoque en Z.
# No hay controles de escala/velocidad en esta página, así que se usan
# valores conservadores por defecto (ajustar según necesidad del laboratorio).
FOCUS_STEP_MM = 0.001        # 1 µm por pulsación
FOCUS_VELOCITY_MM_S = 0.5
FOCUS_ACCEL_MM_S2 = 5.0


class CalibrationPageExtensions:
    """Extensiones de UI para la página de calibración"""

    def __init__(self, ui, main_window, controller):
        self.ui = ui
        self.main = main_window
        # Instancia compartida de AerotechController (ver src/ui_extensions.py)
        self.controller = controller

    def apply_modifications(self):
        """Aplica todas las modificaciones de la página de calibración"""
        self.setup_title()
        self.setup_focusing_section()
        self.setup_calibration_xy_section()
        
    def connect_signals(self):
        """Conecta las señales específicas de la página de calibración"""
        # Las señales ya están conectadas en setup_focusing_section()
        # y setup_calibration_xy_section()
        pass
        
    def setup_title(self):
        """Configura el título de la página"""
        self.ui.label_10.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.label_10.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        
    def setup_focusing_section(self):
        """Configura la sección de enfoque Z"""
        # Título de la sección
        self.ui.label_23.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.label_23.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        
        # Estilo común para botones de enfoque
        focus_button_style = """
            QPushButton {
                background-color: THEME.COLOR_BACKGROUND_2;
                color: THEME.COLOR_TEXT_1;
                border: 2px solid THEME.COLOR_ACCENT_3;
                border-radius: 5px;
                padding: 8px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: THEME.COLOR_ACCENT_2;
                color: white;
                border: 2px solid THEME.COLOR_ACCENT_1;
            }
            QPushButton:pressed {
                background-color: THEME.COLOR_ACCENT_1;
            }
        """
        
        # Botón Z Up
        self.ui.zUpFocusing.setFont(QFont("Sitka Small", 10))
        self.ui.zUpFocusing.setStyleSheet(focus_button_style)
        self.ui.zUpFocusing.setIconSize(QSize(20, 20))
        self.ui.zUpFocusing.setText("Move Up")
        
        # Botón Z Down
        self.ui.zDownFocusing.setFont(QFont("Sitka Small", 10))
        self.ui.zDownFocusing.setStyleSheet(focus_button_style)
        self.ui.zDownFocusing.setIconSize(QSize(20, 20))
        self.ui.zDownFocusing.setText("Move Down")
        
        # Botón Calibrated
        self.ui.calibratedBtn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.calibratedBtn.setStyleSheet("""
            QPushButton {
                background-color: THEME.COLOR_BACKGROUND_2;
                color: THEME.COLOR_TEXT_1;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 10px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
            }
            QPushButton:pressed {
                background-color: #45a049;
            }
        """)
        self.ui.calibratedBtn.setText("Confirm")
        
        # Conectar señales
        self.ui.zUpFocusing.clicked.connect(self.handle_z_up_focusing)
        self.ui.zDownFocusing.clicked.connect(self.handle_z_down_focusing)
        self.ui.calibratedBtn.clicked.connect(self.handle_calibrated)
        
    def setup_calibration_xy_section(self):
        """Configura la sección de calibración X-Y"""
        # Título de la sección
        self.ui.label_24.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.label_24.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        
        # Estilo común para botones de calibración
        calibration_button_style = """
            QPushButton {
                background-color: THEME.COLOR_BACKGROUND_2;
                color: THEME.COLOR_TEXT_1;
                border: 2px solid THEME.COLOR_ACCENT_3;
                border-radius: 8px;
                padding: 10px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #FF9800;
                color: white;
                border: 2px solid #F57C00;
            }
            QPushButton:pressed {
                background-color: #F57C00;
            }
        """
        
        # Botón Zero X
        self.ui.zeroXBtn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.zeroXBtn.setStyleSheet(calibration_button_style)
        self.ui.zeroXBtn.setText("Zero X Position")
        
        # Botón Zero Y
        self.ui.zeroYBtn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.zeroYBtn.setStyleSheet(calibration_button_style)
        self.ui.zeroYBtn.setText("Zero Y Position")
        
        # Conectar señales
        self.ui.zeroXBtn.clicked.connect(self.handle_zero_x)
        self.ui.zeroYBtn.clicked.connect(self.handle_zero_y)
        
    def handle_z_up_focusing(self):
        """Maneja el movimiento Z hacia arriba para enfoque"""
        print("Calibration: Moving Z up for focusing...")
        self.controller.move_relative(AXIS_Z, FOCUS_STEP_MM, FOCUS_VELOCITY_MM_S, FOCUS_ACCEL_MM_S2)

    def handle_z_down_focusing(self):
        """Maneja el movimiento Z hacia abajo para enfoque"""
        print("Calibration: Moving Z down for focusing...")
        self.controller.move_relative(AXIS_Z, -FOCUS_STEP_MM, FOCUS_VELOCITY_MM_S, FOCUS_ACCEL_MM_S2)

    def handle_calibrated(self):
        """Maneja la confirmación de calibración Z"""
        print("Calibration: Z position set as calibrated")
        self.controller.zero_axis(AXIS_Z)

        # Feedback visual
        self.ui.calibratedBtn.setText("✓ Calibrated!")
        self.ui.calibratedBtn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
                border-radius: 8px;
                padding: 10px;
                min-height: 40px;
                font-weight: bold;
            }
        """)
        
    def handle_zero_x(self):
        """Maneja la configuración de X = 0"""
        print("Calibration: Setting X position to zero")
        self.controller.zero_axis(AXIS_X)

        # Feedback visual
        self.ui.zeroXBtn.setText("✓ X = 0 Set")
        self.ui.zeroXBtn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
                border-radius: 8px;
                padding: 10px;
                min-height: 40px;
                font-weight: bold;
            }
        """)
        
    def handle_zero_y(self):
        """Maneja la configuración de Y = 0"""
        print("Calibration: Setting Y position to zero")
        self.controller.zero_axis(AXIS_Y)

        # Feedback visual
        self.ui.zeroYBtn.setText("✓ Y = 0 Set")
        self.ui.zeroYBtn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
                border-radius: 8px;
                padding: 10px;
                min-height: 40px;
                font-weight: bold;
            }
        """)