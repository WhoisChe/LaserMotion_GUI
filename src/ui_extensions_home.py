########################################################################
## HOME PAGE EXTENSIONS
########################################################################

from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy, QGraphicsDropShadowEffect, QFrame
from PySide6.QtGui import QColor

# Colores fijos usados por los LEDs de estado (no dependen del tema visual
# activo, para que el semáforo se lea igual en cualquier tema). Reutilizados
# también por ManualPageExtensions (ver src/ui_extensions_manual.py).
LED_COLOR_OK = "#4CAF50"
LED_COLOR_INACTIVE = "#808080"
LED_COLOR_FAULT = "#F44336"

# Color de texto atenuado cuando no hay conexión (usado si el tema activo no
# define un token de texto secundario).
DISCONNECTED_TEXT_COLOR = "#999999"


class HomePageExtensions:
    """
    Extensiones de UI para la página Home.

    Tras la migración a GlobalStatusPanel (agosto de 2026, ver
    00_global_architecture.md), Home ya no tiene banner de conexión/STO, ni
    LEDs por eje, ni posición X/Y/Z propia — todo eso vive ahora en el panel
    compartido construido en MainWindow (main.py). Lo único que queda aquí
    es la tarjeta "Laser Output" y la imagen de la estación, uno al lado del
    otro.
    """

    def __init__(self, ui, main_window, controller):
        self.ui = ui
        self.main = main_window
        # Instancia compartida de AerotechController (ver main.py)
        self.controller = controller
        self._led_laser_state = None

    def apply_modifications(self):
        """Aplica todas las modificaciones de la página Home"""
        self.setup_laser_card()

    def connect_signals(self):
        """Conecta las señales específicas de la página Home"""
        # Timer propio y ligero: solo refresca la tarjeta de láser (no lee
        # posición — eso ya lo hace el QTimer de MainWindow para el panel
        # global, no hace falta duplicarlo aquí).
        self.laser_card_timer = QTimer()
        self.laser_card_timer.timeout.connect(self.update_laser_card)
        self.laser_card_timer.start(100)

    # ─────────────────────────────────────────────────────────────────────
    # Patrón de LED reutilizable
    # ─────────────────────────────────────────────────────────────────────
    def _make_led(self, color=LED_COLOR_INACTIVE, size=16, tooltip=""):
        """Crea un indicador LED circular (QFrame de tamaño fijo, sin QLineEdit)."""
        led = QFrame()
        led.setObjectName(u"led")
        led.setFixedSize(size, size)
        if tooltip:
            led.setToolTip(tooltip)
        self._set_led_color(led, color)
        return led

    def _set_led_color(self, led, color, dashed_border=False):
        """Cambia el color de un LED ya creado con _make_led(), sin recrearlo.
        dashed_border=True indica un valor aproximado (no medido), ver
        01_home.md §2: 'LED con borde punteado si is_measured es False'."""
        size = led.width()
        border = f"1px dashed {LED_COLOR_INACTIVE}" if dashed_border else "none"
        led.setStyleSheet(
            f"QFrame#led {{ background-color: {color}; border-radius: {size // 2}px; border: {border}; }}"
        )

    # ─────────────────────────────────────────────────────────────────────
    # Actualización periódica (QTimer de 100 ms, ver connect_signals)
    # ─────────────────────────────────────────────────────────────────────
    def update_laser_card(self):
        """Refresca la tarjeta 'Laser Output' con el estado actual del PSO."""
        is_on, duty_percent, power_mw, is_measured = self.controller.get_laser_output_state()
        self._set_led_color(
            self._led_laser_state,
            LED_COLOR_OK if is_on else LED_COLOR_INACTIVE,
            dashed_border=not is_measured,
        )
        self.ui.labelLaserState.setText("ON" if is_on else "OFF")
        self.ui.estadoPotencia.setText(f"{duty_percent:.0f}% · {power_mw:.0f} mW (setpoint)")

    # ─────────────────────────────────────────────────────────────────────
    # Configuración inicial de la interfaz de usuario
    # ─────────────────────────────────────────────────────────────────────
    def setup_laser_card(self):
        """Configura la tarjeta 'Laser Output' (directriz 1.1 de 01_home.md)"""
        self.ui.laserOutputCard.setStyleSheet("""
            QFrame#laserOutputCard {
                max-width: 340px;
            }
        """)

        # Icono
        self.ui.laserIcon.setStyleSheet("""
            QLabel {
                border: none;
            }
        """)

        # Título
        self.ui.laserTitleLabel.setFont(QFont("Sitka Small", 13, QFont.Weight.Bold))
        self.ui.laserTitleLabel.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        self.ui.laserTitleLabel.setText("Laser Output:")

        # Indicador ON/OFF
        self.ui.labelLaserState.setFont(QFont("Sitka Small", 12, QFont.Weight.Bold))
        self.ui.labelLaserState.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        self._led_laser_state = self._make_led(LED_COLOR_INACTIVE, size=20, tooltip="Laser output state")
        self.ui.horizontalLayout_laserState.insertWidget(0, self._led_laser_state)
        self.ui.horizontalLayout_laserState.setSpacing(10)

        # Consigna de potencia
        self.ui.estadoPotencia.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.estadoPotencia.setStyleSheet("""
            QLineEdit#estadoPotencia {
                background-color: transparent;
                color: white;
                font-weight: bold;
                min-width: 260px;
                max-width: 360px;
                min-height: 40px;
                max-height: 40px;
            }
        """)
        self.ui.estadoPotencia.setText("0% · 0 mW (setpoint)")

        # Imagen de la estación, al lado de la tarjeta
        self.ui.estacionAerotech.setMaximumSize(QSize(300, 300))
        self.ui.estacionAerotech.setScaledContents(True)

        # Aplicar sombra a la tarjeta
        self.apply_card_shadow(self.ui.laserOutputCard)

    def apply_card_shadow(self, widget):
        """Aplica efecto de sombra a una tarjeta"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 60))
        widget.setGraphicsEffect(shadow)
