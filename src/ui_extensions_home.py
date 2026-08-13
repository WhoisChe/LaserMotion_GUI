########################################################################
## HOME PAGE EXTENSIONS
########################################################################

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor


class HomePageExtensions:
    """Extensiones de UI para la página Home"""

    def __init__(self, ui, main_window, controller):
        self.ui = ui
        self.main = main_window
        # Instancia compartida de AerotechController (ver src/ui_extensions.py)
        self.controller = controller

    def apply_modifications(self):
        """Aplica todas las modificaciones de la página Home"""
        self.setup_position_status()
        self.setup_status_cards()

    def connect_signals(self):
        """Conecta las señales específicas de la página Home"""
        # Timer para actualizar posición periódicamente
        from PySide6.QtCore import QTimer
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.update_position_display)
        self.position_timer.start(100)  # Actualizar cada 100ms

    # ─────────────────────────────────────────────────────────────────────
    # Modificación de la interfaz de usuario
    # ─────────────────────────────────────────────────────────────────────
    def update_position_display(self):
        """Actualiza la visualización de posición en Home page"""
        # Obtener posición actual del controlador (0,0,0 si no hay conexión)
        x, y, z = self.controller.get_axis_positions()

        # Actualizar labels
        self.ui.valorX.setText(f"{x:.3f}")
        self.ui.valorY.setText(f"{y:.3f}")
        self.ui.valorZ.setText(f"{z:.3f}")

        # Actualizar estado del shutter
        drives_on = self.controller.get_axes_enabled()
        self.update_shutter_display(drives_on)
        
    def update_shutter_display(self, is_open):
        """Actualiza la visualización del estado del shutter"""
        if is_open:
            self.ui.estadoOn.setStyleSheet("""
                QLineEdit {
                    background-color: white;
                    color: #4CAF50;
                    border: 2px solid #45a049;
                    border-radius: 8px;
                    padding: 6px 8px;
                    font-weight: bold;
                }
            """)
            self.ui.estadoOff.setStyleSheet("""
                QLineEdit {
                    background-color: #F7F7F7;
                    color: #E3968A;
                    border: 2px solid #E3968A;
                    border-radius: 8px;
                    padding: 6px 8px;
                }
            """)
        else:
            self.ui.estadoOn.setStyleSheet("""
                QLineEdit {
                    background-color: #F7F7F7;
                    color: #6F9E69;
                    border: 2px solid #6F9E69;
                    border-radius: 8px;
                    padding: 6px 8px;
                }
            """)
            self.ui.estadoOff.setStyleSheet("""
                QLineEdit {
                    background-color: white;
                    color: #F44336;
                    border: 2px solid #DA190B;
                    border-radius: 8px;
                    padding: 6px 8px;
                    font-weight: bold;
                }
            """)
        
    def setup_position_status(self):
        """Configura la visualización del estado de posición"""
        # Configurar labels de posición
        position_labels = [
            (self.ui.label_12, self.ui.valorZ),   # Z position
            (self.ui.label_14, self.ui.valorY),   # Y position
            (self.ui.label_16, self.ui.valorX),   # X position
        ]
        
        for label, value in position_labels:
            # Label del eje
            label.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
            label.setStyleSheet("color: THEME.COLOR_TEXT_1;")
            
            # Valor de la posición
            value.setFont(QFont("Sitka Small", 11))
            value.setStyleSheet("color: THEME.COLOR_ACCENT_3;")
            
        # Ajustar tamaño de la imagen de la estación
        self.ui.estacionAerotech.setMaximumSize(QSize(300, 300))
        self.ui.estacionAerotech.setScaledContents(True)
        
    def setup_status_cards(self):
        """Configura las tarjetas de estado (Shutter y Power)"""
        # Card de Shutter Status
        self.setup_shutter_card()
        
        # Card de Power Status
        self.setup_power_card()
        
    def setup_shutter_card(self):
        """Configura la tarjeta de estado del shutter"""
        # Estilo de la tarjeta usando colores del tema
        self.ui.shutterStatus.setStyleSheet("""
            QFrame#shutterStatus {
                max-width: 250px;
            }
        """)
        
        # Título de la tarjeta
        self.ui.label_18.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.label_18.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        
        # Icono del shutter - colorear según el tema
        self.ui.label.setMaximumSize(QSize(50, 50))
        self.ui.label.setMinimumSize(QSize(50, 50))
        self.ui.label.setStyleSheet("""
            QLabel {
                border: none;
            }
        """)
        
        self.ui.estadoOn.setReadOnly(True)
        self.ui.estadoOn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ui.estadoOn.setFont(QFont("Sitka Small", 9, QFont.Weight.Bold))
        self.ui.estadoOn.setMinimumSize(QSize(80, 32))
        self.ui.estadoOn.setMaximumSize(QSize(80, 32))
        self.ui.estadoOn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.ui.estadoOn.setStyleSheet("""
            QLineEdit#estadoOn {
                background-color: white;
                color: #4CAF50;
                border: 2px solid #45a049;
                border-radius: 8px;
                padding: 6px 8px;
                font-weight: bold;
                min-width: 80px;
                max-width: 80px;
                min-height: 32px;
                max-height: 32px;
            }
        """)
        
        # Estado CLOSED
        self.ui.estadoOff.setReadOnly(True)
        self.ui.estadoOff.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ui.estadoOff.setFont(QFont("Sitka Small", 9, QFont.Weight.Bold))
        self.ui.estadoOff.setMinimumSize(QSize(80, 32))
        self.ui.estadoOff.setMaximumSize(QSize(80, 32))
        self.ui.estadoOff.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.ui.estadoOff.setStyleSheet("""
            QLineEdit#estadoOff {
                background-color: white;
                color: #F44336;
                border: 2px solid #DA190B;
                border-radius: 8px;
                padding: 6px 8px;
                font-weight: bold;
                min-width: 80px;
                max-width: 80px;
                min-height: 32px;
                max-height: 32px;
            }
        """)
        
        # Aplicar sombra a la tarjeta
        self.apply_card_shadow(self.ui.shutterStatus)
        
    def setup_power_card(self):
        """Configura la tarjeta de estado de potencia"""
        # Estilo de la tarjeta usando colores del tema
        self.ui.powerStatus.setStyleSheet("""
            QFrame#powerStatus {
                max-width: 250px;
            }
        """)
        
        # Título de la tarjeta
        self.ui.label_30.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.label_30.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        
        # Icono de potencia
        self.ui.label_34.setMaximumSize(QSize(50, 50))
        self.ui.label_34.setMinimumSize(QSize(50, 50))
        self.ui.label_34.setStyleSheet("""
            QLabel {
                border: none;
            }
        """)
        
        # Campo de visualización de potencia con valor de ejemplo
        self.ui.estadoPower.setReadOnly(True)
        self.ui.estadoPower.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ui.estadoPower.setFont(QFont("Sitka Small", 9, QFont.Weight.Bold))
        self.ui.estadoPower.setMinimumSize(QSize(200, 32))
        self.ui.estadoPower.setMaximumSize(QSize(300, 32))
        self.ui.estadoPower.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Establecer valor de ejemplo
        self.ui.estadoPower.setText("2.5 W")
        
        self.ui.estadoPower.setStyleSheet("""
            QLineEdit#lineEdit {
                background-color: transparent;
                color: white;
                font-weight: bold;
                min-width: 200px;
                max-width: 300px;
                min-height: 32px;
                max-height: 32px;
            }
        """)
        
        # Aplicar sombra a la tarjeta
        self.apply_card_shadow(self.ui.powerStatus)
        
    def apply_card_shadow(self, widget):
        """Aplica efecto de sombra a una tarjeta"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 60))
        widget.setGraphicsEffect(shadow)