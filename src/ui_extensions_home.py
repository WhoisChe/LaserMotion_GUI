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

# Filas de la matriz de estado por eje: (clave interna, etiqueta en español)
AXIS_STATUS_ROWS = [
    ("limit_cw", "Límite CW"),
    ("limit_ccw", "Límite CCW"),
    ("fault", "Fallo"),
    ("homed", "Referenciado"),
]
AXIS_ORDER = ("X", "Y", "Z")


class HomePageExtensions:
    """Extensiones de UI para la página Home"""

    def __init__(self, ui, main_window, controller):
        self.ui = ui
        self.main = main_window
        # Instancia compartida de AerotechController (ver src/ui_extensions.py)
        self.controller = controller

        # Referencias a los LEDs creados dinámicamente, indexadas para poder
        # actualizar su color en cada refresco sin recrearlos.
        self._axis_leds = {}     # {"X": {"limit_cw": QFrame, "limit_ccw": QFrame, "fault": QFrame, "homed": QFrame}, ...}
        self._led_conexion = None
        self._led_sto = None
        self._led_laser_state = None
        self._led_interlock = None

    def apply_modifications(self):
        """Aplica todas las modificaciones de la página Home"""
        self.setup_position_status()
        self.setup_status_banner()
        self.setup_axis_status_card()
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

        # Matriz de LEDs por eje (límites, fallo de posición, referenciado)
        homed = self.controller.get_axes_homed()
        faults = self.controller.get_axis_faults()
        for axis in AXIS_ORDER:
            leds = self._axis_leds[axis]
            axis_faults = faults[axis]
            self._set_led_color(leds["limit_cw"], LED_COLOR_FAULT if axis_faults["limit_cw"] else LED_COLOR_OK)
            self._set_led_color(leds["limit_ccw"], LED_COLOR_FAULT if axis_faults["limit_ccw"] else LED_COLOR_OK)
            self._set_led_color(leds["fault"], LED_COLOR_FAULT if axis_faults["position_error"] else LED_COLOR_OK)
            self._set_led_color(leds["homed"], LED_COLOR_OK if homed[axis] else LED_COLOR_INACTIVE)

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

        for axis in AXIS_ORDER:
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
                f"QFrame#statusBanner {{ background-color: {BANNER_ALERT_COLOR}; border-radius: 12px; }}"
            )
            self.ui.labelSTO.setText("STO ACTIVO")
        else:
            self.ui.statusBanner.setStyleSheet(
                "QFrame#statusBanner { background-color: THEME.COLOR_BACKGROUND_2; border-radius: 12px; }"
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
            label.setFont(QFont("Sitka Small", 13, QFont.Weight.Bold))
            label.setStyleSheet("color: THEME.COLOR_TEXT_1;")

            # Valor de la posición
            value.setFont(QFont("Sitka Small", 15))
            value.setMinimumWidth(110)
            value.setStyleSheet("color: THEME.COLOR_ACCENT_3;")

        # Más aire entre las 3 líneas de posición
        self.ui.verticalLayout_20.setSpacing(16)

        # Ajustar tamaño de la imagen de la estación
        self.ui.estacionAerotech.setMaximumSize(QSize(300, 300))
        self.ui.estacionAerotech.setScaledContents(True)

    def setup_status_banner(self):
        """Configura el banner superior de conexión + STO, agrandado y centrado (directriz 1.2)"""
        self.ui.statusBanner.setStyleSheet(
            "QFrame#statusBanner { background-color: THEME.COLOR_BACKGROUND_2; border-radius: 12px; }"
        )

        for label in (self.ui.labelConexion, self.ui.labelSTO):
            label.setFont(QFont("Sitka Small", 13, QFont.Weight.Bold))
            label.setStyleSheet("color: THEME.COLOR_TEXT_1;")

        self._led_conexion = self._make_led(LED_COLOR_INACTIVE, size=20, tooltip="Estado de conexión con el iSMC")
        self.ui.horizontalLayout_connectionRow.insertWidget(0, self._led_conexion)
        self.ui.horizontalLayout_connectionRow.setSpacing(10)

        self._led_sto = self._make_led(LED_COLOR_INACTIVE, size=20, tooltip="Estado de seguridad (STO)")
        self.ui.horizontalLayout_stoRow.insertWidget(0, self._led_sto)
        self.ui.horizontalLayout_stoRow.setSpacing(10)

        self.ui.labelConexion.setText("Desconectado")
        self.ui.labelSTO.setText("Seguridad OK")

    def setup_axis_status_card(self):
        """Crea la tarjeta intermedia con la matriz de estado por eje (límites,
        fallo de posición y referenciado), entre la imagen de posición y la
        tarjeta de Salida Láser."""
        self.ui.axisStatusCard.setStyleSheet("""
            QFrame#axisStatusCard {
                max-width: 320px;
            }
        """)

        self.ui.axisStatusIcon.setStyleSheet("""
            QLabel {
                border: none;
            }
        """)

        self.ui.axisStatusTitle.setFont(QFont("Sitka Small", 13, QFont.Weight.Bold))
        self.ui.axisStatusTitle.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        self.ui.axisStatusTitle.setText("Estado de Ejes:")

        grid = self.ui.gridLayout_axisStatus

        # Cabecera de columnas: X, Y, Z
        grid.addWidget(QLabel(""), 0, 0)
        for col, axis in enumerate(AXIS_ORDER, start=1):
            header = QLabel(axis)
            header.setFont(QFont("Sitka Small", 12, QFont.Weight.Bold))
            header.setStyleSheet("color: THEME.COLOR_TEXT_1;")
            header.setAlignment(Qt.AlignCenter)
            grid.addWidget(header, 0, col, Qt.AlignCenter)

        # Filas: una por indicador, con un LED por eje
        for axis in AXIS_ORDER:
            self._axis_leds[axis] = {}

        for row, (key, label_text) in enumerate(AXIS_STATUS_ROWS, start=1):
            row_label = QLabel(label_text)
            row_label.setFont(QFont("Sitka Small", 11))
            row_label.setStyleSheet("color: THEME.COLOR_TEXT_1;")
            grid.addWidget(row_label, row, 0, Qt.AlignRight | Qt.AlignVCenter)

            for col, axis in enumerate(AXIS_ORDER, start=1):
                led = self._make_led(LED_COLOR_INACTIVE, size=16, tooltip=f"{label_text} — eje {axis}")
                grid.addWidget(led, row, col, Qt.AlignCenter)
                self._axis_leds[axis][key] = led

        # Aplicar sombra a la tarjeta (mismo patrón visual que las demás)
        self.apply_card_shadow(self.ui.axisStatusCard)

    def setup_laser_card(self):
        """Configura la tarjeta fusionada 'Salida Láser', agrandada (directriz 1.1)"""
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
        self.ui.laserTitleLabel.setText("Salida Láser:")

        # Indicador ON/OFF
        self.ui.labelLaserState.setFont(QFont("Sitka Small", 12, QFont.Weight.Bold))
        self.ui.labelLaserState.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        self._led_laser_state = self._make_led(LED_COLOR_INACTIVE, size=20, tooltip="Estado de salida del láser")
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
        self.ui.estadoPotencia.setText("0% · 0 mW (consigna)")

        # Slot de interlock — permanece en gris fijo mientras
        # config.LASER_INTERLOCK_AVAILABLE sea False (directriz 2.2)
        self.ui.labelInterlock.setFont(QFont("Sitka Small", 10))
        self.ui.labelInterlock.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        interlock_tooltip = "Interlock del láser" if config.LASER_INTERLOCK_AVAILABLE else "Interlock no disponible todavía"
        self._led_interlock = self._make_led(LED_COLOR_INACTIVE, size=20, tooltip=interlock_tooltip)
        self.ui.horizontalLayout_laserInterlock.insertWidget(0, self._led_interlock)
        self.ui.horizontalLayout_laserInterlock.setSpacing(10)
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
