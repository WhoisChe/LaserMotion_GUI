########################################################################
## MANUAL PAGE EXTENSIONS
########################################################################

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import QSizePolicy, QGraphicsDropShadowEffect, QMessageBox
from PySide6.QtGui import QColor

from src.aerotech_controller import AXIS_X, AXIS_Y, AXIS_Z

# Salida digital que controla el shutter del láser. AJUSTAR al cableado
# real de la estación (eje del drive y número de salida digital usados).
SHUTTER_OUTPUT_AXIS = AXIS_X
SHUTTER_OUTPUT_NUM = 0


class ManualPageExtensions:
    """Extensiones de UI para la página Manual Mode"""

    def __init__(self, ui, main_window, controller):
        self.ui = ui
        self.main = main_window
        # Instancia compartida de AerotechController (ver src/ui_extensions.py)
        self.controller = controller

    def apply_modifications(self):
        """Aplica todas las modificaciones de la página Manual"""
        self.setup_movement_section()
        self.setup_shutter_section()

    def connect_signals(self):
        """Conecta las señales específicas de la página Manual"""
        # Botones de movimiento XY
        self.ui.xyUpBtn.clicked.connect(self.move_y_positive)
        self.ui.xyDownBtn.clicked.connect(self.move_y_negative)
        self.ui.xyLeftBtn.clicked.connect(self.move_x_negative)
        self.ui.xyRightBtn.clicked.connect(self.move_x_positive)
        self.ui.xyZeroBtn.clicked.connect(self.move_xy_zero)
        
        # Botones de movimiento Z
        self.ui.zUpBtn.clicked.connect(self.move_z_positive)
        self.ui.zDownBtn.clicked.connect(self.move_z_negative)
        
        # Cambio de escala
        self.ui.scaleList.currentIndexChanged.connect(self.on_scale_changed)
        
        # Botón de confirmación
        self.ui.confirmBtn.clicked.connect(self.confirm_values)

        # Los botones de shutter ya están conectados en setup_shutter_section()
        
    # ─────────────────────────────────────────────────────────────────────
    # Conexión al controlador Automation1-iSMC via API - Funciones de movimiento
    # ─────────────────────────────────────────────────────────────────────
    # Movimiento relativo (delega en AerotechController.move_relative)
    # ─────────────────────────────────────────────────────────────────────
    def _move_relative(self, axis, distance_mm, velocity, acceleration):
        """
        Ejecuta un movimiento relativo en un eje del ANT130XY/ANT130LZS.
        - axis: nombre del eje ("X", "Y" o "Z")
        - distance_mm: desplazamiento en mm (positivo o negativo)
        - velocity: velocidad en mm/s
        - acceleration: aceleración en mm/s²
        """
        self.controller.move_relative(axis, distance_mm, velocity, acceleration)

    def move_x_positive(self):
        """Mueve X en dirección positiva"""
        scale = self.get_current_scale()
        velocity = self.ui.velocity.value()
        acceleration = self.ui.acceleration.value()
        
        print(f"Moving X+ | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_X, scale, velocity, acceleration)
        
    def move_x_negative(self):
        """Mueve X en dirección negativa"""
        scale = self.get_current_scale()
        velocity = self.ui.velocity.value()
        acceleration = self.ui.acceleration.value()
        
        print(f"Moving X- | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_X, -scale, velocity, acceleration) 
        
    def move_y_positive(self):
        """Mueve Y en dirección positiva"""
        scale = self.get_current_scale()
        velocity = self.ui.velocity.value()
        acceleration = self.ui.acceleration.value()
        
        print(f"Moving Y+ | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_Y, scale, velocity, acceleration)
        
    def move_y_negative(self):
        """Mueve Y en dirección negativa"""
        scale = self.get_current_scale()
        velocity = self.ui.velocity.value()
        acceleration = self.ui.acceleration.value()
        
        print(f"Moving Y- | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_Y, -scale, velocity, acceleration)
        
    def move_z_positive(self):
        """Mueve Z en dirección positiva"""
        scale = self.get_current_scale()
        velocity = self.ui.velocity.value()
        acceleration = self.ui.acceleration.value()
        
        print(f"Moving Z+ | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_Z, scale, velocity, acceleration)

    def move_z_negative(self):
        """Mueve Z en dirección negativa"""
        scale = self.get_current_scale()
        velocity = self.ui.velocity.value()
        acceleration = self.ui.acceleration.value()
        
        print(f"Moving Z- | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_Z, -scale, velocity, acceleration) 
        
    def move_xy_zero(self):
        """Mueve XY a posición cero"""
        velocity = self.ui.velocity.value()
        acceleration = self.ui.acceleration.value()

        print(f"Moving to XY Zero | Vel: {velocity} | Acc: {acceleration}")
        self.controller.move_absolute([AXIS_X, AXIS_Y], [0.0, 0.0], velocity, acceleration)


    # ─────────────────────────────────────────────────────────────────────
    # Modificación de la interfaz de usuario
    # ─────────────────────────────────────────────────────────────────────        
    def get_current_scale(self):
        """Obtiene el valor de escala actual en mm"""
        scale_value = self.ui.scaleList.currentData()
        
        # Convertir a mm
        conversions = {
            "nm": 0.000001,
            "μm": 0.001,
            "mm": 1.0,
            "cm": 10.0
        }
        
        return conversions.get(scale_value, 1.0)
        
    def on_scale_changed(self):
        """Maneja el cambio de escala"""
        scale = self.ui.scaleList.currentText()
        print(f"Scale changed to: {scale}")
        
    def setup_movement_section(self):
        """Configura la sección de movimiento XYZ"""
        # Título de Moviviento XYZ
        self.ui.label_19.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.label_19.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        
        # Configurar selector de escala, velocidad y aceleración
        self.ui.label_31.setFont(QFont("Sitka Small", 10))
        self.setup_scale_selector()
        self.ui.label_32.setFont(QFont("Sitka Small", 10))
        self.setup_velocity_selector()
        self.ui.label_33.setFont(QFont("Sitka Small", 10))
        self.setup_acceleration_selector()
        
    def setup_scale_selector(self):
        """Configura el selector de escala"""
        # Limpiar items existentes
        self.ui.scaleList.clear()
        
        # Añadir opciones de escala de menor a mayor
        scales = [
            ("nm", "Nanómetros (nm)"),
            ("μm", "Micrómetros (μm)"),
            ("mm", "Milímetros (mm)"),
            ("cm", "Centímetros (cm)")
        ]
        
        for value, text in scales:
            self.ui.scaleList.addItem(text, value)
        
        # Seleccionar mm por defecto
        self.ui.scaleList.setCurrentIndex(2)
        
        # Estilo
        self.ui.scaleList.setFont(QFont("Sitka Small", 10))   
        
    def setup_velocity_selector(self):
        """Configura el selector de velocidad"""
        self.ui.velocity.setFont(QFont("Sitka Small", 10))
        self.ui.velocity.setMinimum(0.1)
        self.ui.velocity.setMaximum(1000.0)
        self.ui.velocity.setSingleStep(0.1)
        self.ui.velocity.setDecimals(2)
        self.ui.velocity.setSuffix(" mm/s")
        self.ui.velocity.setValue(10.0)
          
    def setup_acceleration_selector(self):
        """Configura el selector de aceleración"""
        self.ui.acceleration.setFont(QFont("Sitka Small", 10))
        self.ui.acceleration.setMinimum(0.1)
        self.ui.acceleration.setMaximum(10000.0)
        self.ui.acceleration.setSingleStep(1.0)
        self.ui.acceleration.setDecimals(2)
        self.ui.acceleration.setSuffix(" mm/s²")
        self.ui.acceleration.setValue(100.0)
    
    def confirm_values(self):
        """Muestra mensaje de confirmación cuando se oprimen los valores de velocidad y aceleración"""
        velocity = self.ui.velocity.value()
        acceleration = self.ui.acceleration.value()
        
        # Crear mensaje box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Valores Guardados")
        msg.setText(f"Los valores han sido guardados correctamente:")
        msg.setInformativeText(f"Velocidad: {velocity} mm/s\nAceleración: {acceleration} mm/s²")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def setup_shutter_section(self):
        """Configura la sección del shutter"""
        
        # Botón OPEN
        self.ui.openShutterBtn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.openShutterBtn.setMinimumHeight(60)
        self.ui.openShutterBtn.setMinimumWidth(150)
        self.ui.openShutterBtn.setCheckable(True)
        
        # Botón CLOSE
        self.ui.closeShutterBtn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.closeShutterBtn.setMinimumHeight(60)
        self.ui.closeShutterBtn.setMinimumWidth(150)
        self.ui.closeShutterBtn.setCheckable(True)
    
        # Configurar estilo inicial del ícono laserOC (color por defecto de íconos)
        self.update_laser_icon_color(None)
        
        # Conectar señales para que sean mutuamente exclusivos
        self.ui.openShutterBtn.clicked.connect(
            lambda: self.handle_shutter_button_click(True)
        )
        self.ui.closeShutterBtn.clicked.connect(
            lambda: self.handle_shutter_button_click(False)
        )
        
    def handle_shutter_button_click(self, is_open):
        """Maneja el clic de los botones del shutter"""
        if is_open:
            if self.ui.openShutterBtn.isChecked():
                self.ui.closeShutterBtn.setChecked(False)
                self.update_laser_icon_color("green")
                self.controller.set_digital_output(SHUTTER_OUTPUT_AXIS, SHUTTER_OUTPUT_NUM, True)
            else:
                self.update_laser_icon_color(None)
        else:
            if self.ui.closeShutterBtn.isChecked():
                self.ui.openShutterBtn.setChecked(False)
                self.update_laser_icon_color("red")
                self.controller.set_digital_output(SHUTTER_OUTPUT_AXIS, SHUTTER_OUTPUT_NUM, False)
            else:
                self.update_laser_icon_color(None)
    
    def update_laser_icon_color(self, color):
        """Actualiza el color del ícono laserOC
        Args:
            color: 'green' para abierto, 'red' para cerrado
        """
        if color == "green":
            # Verde cuando está abierto
            self.ui.laserOC.setStyleSheet("""
                QLabel#laserOC {
                    background-color: #4CAF50;
                    border-radius: 60%;
                }
            """)
        elif color == "red":
            # Rojo cuando está cerrado
            self.ui.laserOC.setStyleSheet("""
                QLabel#laserOC {
                    background-color: #F44336;
                    border-radius: 60%;
                }
            """)
        else:
            # Color por defecto (color de íconos del tema)
            self.ui.laserOC.setStyleSheet("""
                QLabel#laserOC {
                    background-color: none;
                    border-radius: 60%;
                }
            """)