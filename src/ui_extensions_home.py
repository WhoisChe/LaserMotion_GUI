########################################################################
## HOME PAGE EXTENSIONS
########################################################################

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy, QGraphicsDropShadowEffect, QFrame, QLabel
from PySide6.QtGui import QColor

import config

# Colores fijos usados por los LEDs de estado (no dependen del tema visual
# activo, para que el semáforo se lea igual en cualquier tema).
LED_COLOR_OK = "#4CAF50"
LED_COLOR_INACTIVE = "#808080"
LED_COLOR_FAULT = "#F44336"

# Color de texto/posición atenuado cuando no hay conexión (usado si el tema
# activo no define un token de texto secundario).
DISCONNECTED_TEXT_COLOR = "#999999"

# Rojo de alerta fijo del banner cuando el STO está activo (no depende del tema).
BANNER_ALERT_COLOR = "#DA190B"


class HomePageExtensions:
    """Extensiones de UI para la página Home"""

    def __init__(self, ui, main_window, controller):
        self.ui = ui
        self.main = main_window
        # Instancia compartida de AerotechController (ver src/ui_extensions.py)
        self.controller = controller

        # Referencias a los LEDs creados dinámicamente, indexadas para poder
        # actualizar su color en cada refresco sin recrearlos.
        self._axis_leds = {}     # {"X": {"enabled": QFrame, "homed": QFrame, "no_pos_error": QFrame, "limits_free": QFrame}, ...}
        self._led_conexion = None
        self._led_sto = None
        self._led_laser_state = None
        self._led_interlock = None

    def apply_modifications(self):
        """Aplica todas las modificaciones de la página Home"""
        self.setup_position_status()
        self.setup_status_banner()
        self.setup_axis_led_rows()
        self.setup_laser_card()

    def connect_signals(self):
        """Conecta las señales específicas de la página Home"""
        # Timer para actualizar posición periódicamente
        from PySide6.QtCore import QTimer
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.update_position_display)
        self.position_timer.start(100)  # Actualizar cada 100ms

    # ─────────────────────────────────────────────────────────────────────
    # Patrón de LED reutilizable (ver directrices 1.5)
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

    def _set_led_color(self, led, color):
        """Cambia el color de un LED ya creado con _make_led(), sin recrearlo."""
        size = led.width()
        led.setStyleSheet(
            f"QFrame#led {{ background-color: {color}; border-radius: {size // 2}px; }}"
        )

    # ─────────────────────────────────────────────────────────────────────
    # Actualización periódica (QTimer de 100 ms, ver connect_signals)
    # ─────────────────────────────────────────────────────────────────────
    def update_position_display(self):
        """Actualiza toda la página Home: posición, banner, LEDs y tarjeta de láser."""
        if not self.controller.is_connected:
            self._show_disconnected_state()
            return

        # Posición
        x, y, z = self.controller.get_axis_positions()
        self.ui.valorX.setText(f"{x:.3f}")
        self.ui.valorY.setText(f"{y:.3f}")
        self.ui.valorZ.setText(f"{z:.3f}")
        self._set_position_text_color(None)  # color normal del tema

        # Banner de conexión
        self._set_led_color(self._led_conexion, LED_COLOR_OK)
        self.ui.labelConexion.setText(f"Conectado — {self.controller.host}")

        # Banner de STO
        sto_active = self.controller.get_sto_status()
        self._update_sto_banner(sto_active)

        # LEDs por eje (habilitación, homing, error de posición, límites)
        # NOTA: get_axes_enabled() devuelve un único booleano combinado para
        # los 3 ejes (no hay lectura individual por eje en la API actual), así
        # que se aplica el mismo valor al indicador "Habilitado" de cada eje.
        enabled = self.controller.get_axes_enabled()
        homed = self.controller.get_axes_homed()
        faults = self.controller.get_axis_faults()
        for axis in ("X", "Y", "Z"):
            leds = self._axis_leds[axis]
            axis_faults = faults[axis]
            self._set_led_color(leds["enabled"], LED_COLOR_OK if enabled else LED_COLOR_INACTIVE)
            self._set_led_color(leds["homed"], LED_COLOR_OK if homed[axis] else LED_COLOR_INACTIVE)
            self._set_led_color(
                leds["no_pos_error"],
                LED_COLOR_FAULT if axis_faults["position_error"] else LED_COLOR_OK,
            )
            limits_ok = not (axis_faults["limit_cw"] or axis_faults["limit_ccw"])
            self._set_led_color(leds["limits_free"], LED_COLOR_OK if limits_ok else LED_COLOR_FAULT)

        # Tarjeta de Salida Láser
        is_on, duty_percent, power_mw = self.controller.get_laser_output_state()
        self._set_led_color(self._led_laser_state, LED_COLOR_OK if is_on else LED_COLOR_INACTIVE)
        self.ui.labelLaserState.setText("ON" if is_on else "OFF")
        self.ui.estadoPotencia.setText(f"{duty_percent:.0f}% · {power_mw:.0f} mW (consigna)")
        # El LED de interlock solo refleja dato real si config.LASER_INTERLOCK_AVAILABLE
        # es True; de lo contrario se mantiene en gris fijo (ver setup_laser_card).

    def _show_disconnected_state(self):
        """Pinta la página Home en el estado 'sin conexión' (ver directriz 1.4 y 2.3)."""
        self.ui.valorX.setText("—")
        self.ui.valorY.setText("—")
        self.ui.valorZ.setText("—")
        self._set_position_text_color(DISCONNECTED_TEXT_COLOR)

        self._set_led_color(self._led_conexion, LED_COLOR_FAULT)
        self.ui.labelConexion.setText("Desconectado")

        self._update_sto_banner(False)

        for axis in ("X", "Y", "Z"):
            for led in self._axis_leds[axis].values():
                self._set_led_color(led, LED_COLOR_INACTIVE)

        self._set_led_color(self._led_laser_state, LED_COLOR_INACTIVE)
        self.ui.labelLaserState.setText("OFF")
        self.ui.estadoPotencia.setText("0% · 0 mW (consigna)")

    def _set_position_text_color(self, color):
        """color=None restaura el color normal del tema; si no, aplica un color fijo."""
        style = f"color: {color};" if color else "color: THEME.COLOR_ACCENT_3;"
        for value in (self.ui.valorX, self.ui.valorY, self.ui.valorZ):
            value.setStyleSheet(style)

    def _update_sto_banner(self, sto_active):
        if sto_active:
            self.ui.statusBanner.setStyleSheet(
                f"QFrame#statusBanner {{ background-color: {BANNER_ALERT_COLOR}; border-radius: 8px; }}"
            )
            self.ui.labelSTO.setText("STO ACTIVO")
        else:
            self.ui.statusBanner.setStyleSheet(
                "QFrame#statusBanner { background-color: THEME.COLOR_BACKGROUND_2; border-radius: 8px; }"
            )
            self.ui.labelSTO.setText("Seguridad OK")
        self._set_led_color(self._led_sto, LED_COLOR_FAULT if sto_active else LED_COLOR_OK)

    # ─────────────────────────────────────────────────────────────────────
    # Configuración inicial de la interfaz de usuario
    # ─────────────────────────────────────────────────────────────────────
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

    def setup_status_banner(self):
        """Configura el banner superior de conexión + STO (directriz 1.2)"""
        self.ui.statusBanner.setStyleSheet(
            "QFrame#statusBanner { background-color: THEME.COLOR_BACKGROUND_2; border-radius: 8px; }"
        )

        for label in (self.ui.labelConexion, self.ui.labelSTO):
            label.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
            label.setStyleSheet("color: THEME.COLOR_TEXT_1;")

        self._led_conexion = self._make_led(LED_COLOR_INACTIVE, size=16, tooltip="Estado de conexión con el iSMC")
        self.ui.horizontalLayout_connectionRow.insertWidget(0, self._led_conexion)

        self._led_sto = self._make_led(LED_COLOR_INACTIVE, size=16, tooltip="Estado de seguridad (STO)")
        self.ui.horizontalLayout_stoRow.insertWidget(0, self._led_sto)

        self.ui.labelConexion.setText("Desconectado")
        self.ui.labelSTO.setText("Seguridad OK")

    def setup_axis_led_rows(self):
        """Crea los 4 LEDs de estado (Habilitado, Homed, Sin error de posición,
        Límites libres) para cada uno de los 3 ejes (directriz 1.3)."""
        led_specs = [
            ("enabled", "Habilitado"),
            ("homed", "Homed"),
            ("no_pos_error", "Sin error de posición"),
            ("limits_free", "Límites libres"),
        ]
        axis_layouts = {
            "X": self.ui.horizontalLayout_ledRowX,
            "Y": self.ui.horizontalLayout_ledRowY,
            "Z": self.ui.horizontalLayout_ledRowZ,
        }

        for axis, layout in axis_layouts.items():
            self._axis_leds[axis] = {}
            for key, tooltip in led_specs:
                led = self._make_led(LED_COLOR_INACTIVE, size=12, tooltip=tooltip)
                layout.addWidget(led)
                self._axis_leds[axis][key] = led

    def setup_laser_card(self):
        """Configura la tarjeta fusionada 'Salida Láser' (directriz 1.1)"""
        self.ui.laserOutputCard.setStyleSheet("""
            QFrame#laserOutputCard {
                max-width: 250px;
            }
        """)

        # Icono
        self.ui.laserIcon.setMaximumSize(QSize(50, 50))
        self.ui.laserIcon.setMinimumSize(QSize(50, 50))
        self.ui.laserIcon.setStyleSheet("""
            QLabel {
                border: none;
            }
        """)

        # Título
        self.ui.laserTitleLabel.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.laserTitleLabel.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        self.ui.laserTitleLabel.setText("Salida Láser:")

        # Indicador ON/OFF
        self.ui.labelLaserState.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.labelLaserState.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        self._led_laser_state = self._make_led(LED_COLOR_INACTIVE, size=16, tooltip="Estado de salida del láser")
        self.ui.horizontalLayout_laserState.insertWidget(0, self._led_laser_state)

        # Consigna de potencia
        self.ui.estadoPotencia.setFont(QFont("Sitka Small", 9, QFont.Weight.Bold))
        self.ui.estadoPotencia.setStyleSheet("""
            QLineEdit#estadoPotencia {
                background-color: transparent;
                color: white;
                font-weight: bold;
                min-width: 200px;
                max-width: 300px;
                min-height: 32px;
                max-height: 32px;
            }
        """)
        self.ui.estadoPotencia.setText("0% · 0 mW (consigna)")

        # Slot de interlock — permanece en gris fijo mientras
        # config.LASER_INTERLOCK_AVAILABLE sea False (directriz 2.2)
        self.ui.labelInterlock.setFont(QFont("Sitka Small", 9))
        self.ui.labelInterlock.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        interlock_tooltip = "Interlock del láser" if config.LASER_INTERLOCK_AVAILABLE else "Interlock no disponible todavía"
        self._led_interlock = self._make_led(LED_COLOR_INACTIVE, size=16, tooltip=interlock_tooltip)
        self.ui.horizontalLayout_laserInterlock.insertWidget(0, self._led_interlock)
        self.ui.labelInterlock.setText("Interlock: N/D")

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
