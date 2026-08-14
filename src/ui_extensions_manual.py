########################################################################
## MANUAL PAGE EXTENSIONS
########################################################################

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMessageBox

from src.aerotech_controller import AXIS_X, AXIS_Y, AXIS_Z
from src.ui_extensions_home import HomePageExtensions, LED_COLOR_OK, LED_COLOR_INACTIVE, LED_COLOR_FAULT, DISCONNECTED_TEXT_COLOR

AXIS_CONST = {"X": AXIS_X, "Y": AXIS_Y, "Z": AXIS_Z}

# Borde naranja para Velocity/Acceleration mientras el valor en pantalla no
# coincide con el valor realmente aplicado a los movimientos (ver 2.3).
PENDING_BORDER_STYLE = "QDoubleSpinBox { border: 2px solid #FFA726; }"


class ManualPageExtensions:
    """Extensiones de UI para la página Manual Mode"""

    def __init__(self, ui, main_window, controller):
        self.ui = ui
        self.main = main_window
        # Instancia compartida de AerotechController (ver src/ui_extensions.py)
        self.controller = controller

        # LEDs de estado por eje (Habilitado, Homed, Sin error de posición,
        # Límites libres), indexados para poder actualizar su color sin recrearlos.
        self._axis_leds = {}

        # Valores de velocidad/aceleración realmente aplicados a los
        # movimientos — distintos de lo que muestren los spinbox mientras
        # haya cambios sin confirmar (ver 2.3).
        self._applied_velocity = 10.0
        self._applied_acceleration = 100.0

    def apply_modifications(self):
        """Aplica todas las modificaciones de la página Manual"""
        self.setup_axis_control_section()
        self.setup_position_manual()
        self.setup_movement_section()
        self.setup_laser_power_section()

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

        # Compuerta de confirmación de velocity/acceleration
        self.ui.confirmBtn.clicked.connect(self.confirm_values)
        self.ui.velocity.valueChanged.connect(self._check_pending_changes)
        self.ui.acceleration.valueChanged.connect(self._check_pending_changes)

        # Control por eje: enable/disable + home
        self.ui.toggleXBtn.clicked.connect(lambda: self.handle_toggle_axis("X"))
        self.ui.toggleYBtn.clicked.connect(lambda: self.handle_toggle_axis("Y"))
        self.ui.toggleZBtn.clicked.connect(lambda: self.handle_toggle_axis("Z"))
        self.ui.homeXBtn.clicked.connect(lambda: self.controller.home_axes([AXIS_X]))
        self.ui.homeYBtn.clicked.connect(lambda: self.controller.home_axes([AXIS_Y]))
        self.ui.homeZBtn.clicked.connect(lambda: self.controller.home_axes([AXIS_Z]))

        # Control de potencia del láser (en vivo, sin compuerta de confirmación)
        self.ui.laserPowerSlider.valueChanged.connect(self.handle_laser_power_changed)
        self.ui.laserOffBtn.clicked.connect(lambda: self.ui.laserPowerSlider.setValue(0))

        # Refresco periódico de posición y LEDs de estado por eje
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_display)
        self.status_timer.start(100)  # Mismo intervalo que Home

    # ─────────────────────────────────────────────────────────────────────
    # LED reutilizado de la página Home (ver directriz 1.1: "no duplicar la
    # construcción del LED"). _make_led()/_set_led_color() de HomePageExtensions
    # no usan ningún atributo de instancia (self.ui/self.controller), así que
    # se pueden invocar pasando esta instancia de ManualPageExtensions como
    # "self" sin heredar de esa clase ni copiar la lógica de dibujo del LED.
    # ─────────────────────────────────────────────────────────────────────
    def _make_led(self, *args, **kwargs):
        return HomePageExtensions._make_led(self, *args, **kwargs)

    def _set_led_color(self, *args, **kwargs):
        return HomePageExtensions._set_led_color(self, *args, **kwargs)

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
        velocity = self._applied_velocity
        acceleration = self._applied_acceleration

        print(f"Moving X+ | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_X, scale, velocity, acceleration)

    def move_x_negative(self):
        """Mueve X en dirección negativa"""
        scale = self.get_current_scale()
        velocity = self._applied_velocity
        acceleration = self._applied_acceleration

        print(f"Moving X- | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_X, -scale, velocity, acceleration)

    def move_y_positive(self):
        """Mueve Y en dirección positiva"""
        scale = self.get_current_scale()
        velocity = self._applied_velocity
        acceleration = self._applied_acceleration

        print(f"Moving Y+ | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_Y, scale, velocity, acceleration)

    def move_y_negative(self):
        """Mueve Y en dirección negativa"""
        scale = self.get_current_scale()
        velocity = self._applied_velocity
        acceleration = self._applied_acceleration

        print(f"Moving Y- | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_Y, -scale, velocity, acceleration)

    def move_z_positive(self):
        """Mueve Z en dirección positiva"""
        scale = self.get_current_scale()
        velocity = self._applied_velocity
        acceleration = self._applied_acceleration

        print(f"Moving Z+ | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_Z, scale, velocity, acceleration)

    def move_z_negative(self):
        """Mueve Z en dirección negativa"""
        scale = self.get_current_scale()
        velocity = self._applied_velocity
        acceleration = self._applied_acceleration

        print(f"Moving Z- | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_Z, -scale, velocity, acceleration)

    def move_xy_zero(self):
        """Mueve XY a posición cero"""
        velocity = self._applied_velocity
        acceleration = self._applied_acceleration

        print(f"Moving to XY Zero | Vel: {velocity} | Acc: {acceleration}")
        self.controller.move_absolute([AXIS_X, AXIS_Y], [0.0, 0.0], velocity, acceleration)

    # ─────────────────────────────────────────────────────────────────────
    # Control por eje: Enable/Disable + Home (directriz 2.1)
    # ─────────────────────────────────────────────────────────────────────
    def handle_toggle_axis(self, axis):
        """Alterna habilitación/deshabilitación de un único eje (patrón de connectBtn)."""
        btn = {"X": self.ui.toggleXBtn, "Y": self.ui.toggleYBtn, "Z": self.ui.toggleZBtn}[axis]
        axis_const = AXIS_CONST[axis]
        if btn.isChecked():
            self.controller.enable_axes([axis_const])
            btn.setText("DISABLE")
        else:
            self.controller.disable_axes([axis_const])
            btn.setText("ENABLE")

    # ─────────────────────────────────────────────────────────────────────
    # Refresco periódico de estado (posición, fallos, homed) — directriz 2.2
    # ─────────────────────────────────────────────────────────────────────
    def update_status_display(self):
        """Misma lógica que HomePageExtensions.update_position_display(), aplicada
        a los widgets propios de la página Manual."""
        if not self.controller.is_connected:
            self._show_disconnected_status()
            return

        x, y, z = self.controller.get_axis_positions()
        self.ui.valorXManual.setText(f"{x:.3f}")
        self.ui.valorYManual.setText(f"{y:.3f}")
        self.ui.valorZManual.setText(f"{z:.3f}")
        self._set_position_text_color(None)

        # NOTA: get_axes_enabled() devuelve un único booleano combinado para
        # los 3 ejes (no hay lectura individual por eje en la API actual), así
        # que el LED "Habilitado" de X, Y y Z muestra ese mismo valor.
        enabled = self.controller.get_axes_enabled()
        homed = self.controller.get_axes_homed()
        faults = self.controller.get_axis_faults()
        for axis in ("X", "Y", "Z"):
            leds = self._axis_leds[axis]
            axis_faults = faults[axis]
            self._set_led_color(leds["enabled"], LED_COLOR_OK if enabled else LED_COLOR_INACTIVE)
            self._set_led_color(leds["homed"], LED_COLOR_OK if homed[axis] else LED_COLOR_INACTIVE)
            self._set_led_color(leds["fault"], LED_COLOR_FAULT if axis_faults["position_error"] else LED_COLOR_OK)
            limits_ok = not (axis_faults["limit_cw"] or axis_faults["limit_ccw"])
            self._set_led_color(leds["limits"], LED_COLOR_OK if limits_ok else LED_COLOR_FAULT)

    def _show_disconnected_status(self):
        self.ui.valorXManual.setText("—")
        self.ui.valorYManual.setText("—")
        self.ui.valorZManual.setText("—")
        self._set_position_text_color(DISCONNECTED_TEXT_COLOR)

        for axis in ("X", "Y", "Z"):
            for led in self._axis_leds[axis].values():
                self._set_led_color(led, LED_COLOR_INACTIVE)

    def _set_position_text_color(self, color):
        style = f"color: {color};" if color else "color: THEME.COLOR_ACCENT_3;"
        for value in (self.ui.valorXManual, self.ui.valorYManual, self.ui.valorZManual):
            value.setStyleSheet(style)

    # ─────────────────────────────────────────────────────────────────────
    # Modificación de la interfaz de usuario
    # ─────────────────────────────────────────────────────────────────────
    def get_current_scale(self):
        """Obtiene el paso de jog en mm: escala del scaleList × scaleMultiplier."""
        scale_value = self.ui.scaleList.currentData()

        # Convertir a mm
        conversions = {
            "nm": 0.000001,
            "μm": 0.001,
            "mm": 1.0,
            "cm": 10.0
        }

        base = conversions.get(scale_value, 1.0)
        return base * self.ui.scaleMultiplier.value()

    def on_scale_changed(self):
        """Maneja el cambio de escala"""
        scale = self.ui.scaleList.currentText()
        print(f"Scale changed to: {scale}")

    def setup_axis_control_section(self):
        """Configura los 3 bloques de control por eje (Enable/Disable, Home, LEDs)"""
        axis_specs = [
            ("X", self.ui.labelAxisX, self.ui.toggleXBtn, self.ui.homeXBtn, self.ui.horizontalLayout_ledManualX),
            ("Y", self.ui.labelAxisY, self.ui.toggleYBtn, self.ui.homeYBtn, self.ui.horizontalLayout_ledManualY),
            ("Z", self.ui.labelAxisZ, self.ui.toggleZBtn, self.ui.homeZBtn, self.ui.horizontalLayout_ledManualZ),
        ]
        led_specs = [
            ("enabled", "Habilitado"),
            ("homed", "Homed"),
            ("fault", "Sin error de posición"),
            ("limits", "Límites libres"),
        ]

        toggle_style = """
            QPushButton {
                background-color: THEME.COLOR_BACKGROUND_2;
                color: THEME.COLOR_TEXT_1;
                border: 2px solid THEME.COLOR_ACCENT_3;
                border-radius: 8px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: THEME.COLOR_ACCENT_2;
                color: white;
                border: 2px solid THEME.COLOR_ACCENT_1;
            }
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
            }
        """
        home_style = """
            QPushButton {
                background-color: THEME.COLOR_BACKGROUND_2;
                color: THEME.COLOR_TEXT_1;
                border: 2px solid THEME.COLOR_ACCENT_3;
                border-radius: 8px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: THEME.COLOR_ACCENT_1;
                color: white;
            }
        """

        for axis, label, toggle_btn, home_btn, led_layout in axis_specs:
            label.setFont(QFont("Sitka Small", 13, QFont.Weight.Bold))
            label.setStyleSheet("color: THEME.COLOR_TEXT_1;")

            toggle_btn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
            toggle_btn.setMinimumHeight(40)
            toggle_btn.setStyleSheet(toggle_style)
            toggle_btn.setText("ENABLE")

            home_btn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
            home_btn.setMinimumHeight(36)
            home_btn.setStyleSheet(home_style)

            self._axis_leds[axis] = {}
            for key, tooltip in led_specs:
                led = self._make_led(LED_COLOR_INACTIVE, size=12, tooltip=f"{tooltip} — eje {axis}")
                led_layout.addWidget(led)
                self._axis_leds[axis][key] = led

    def setup_position_manual(self):
        """Configura la posición en vivo X/Y/Z junto al D-pad (mismo formato que Home)"""
        position_labels = [
            (self.ui.labelPosManualX, self.ui.valorXManual),
            (self.ui.labelPosManualY, self.ui.valorYManual),
            (self.ui.labelPosManualZ, self.ui.valorZManual),
        ]
        for label, value in position_labels:
            label.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
            label.setStyleSheet("color: THEME.COLOR_TEXT_1;")
            value.setFont(QFont("Sitka Small", 12))
            value.setMinimumWidth(80)
            value.setStyleSheet("color: THEME.COLOR_ACCENT_3;")
            value.setText("—")

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
        """Configura el selector de escala y su multiplicador ×N"""
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

        # Multiplicador ×N (directriz 1.3)
        self.ui.scaleMultiplier.setFont(QFont("Sitka Small", 10))
        self.ui.scaleMultiplier.setToolTip("Multiplicador del paso de jog (escala × N)")

    def setup_velocity_selector(self):
        """Configura el selector de velocidad"""
        self.ui.velocity.setFont(QFont("Sitka Small", 10))
        self.ui.velocity.setMinimum(0.1)
        self.ui.velocity.setMaximum(1000.0)
        self.ui.velocity.setSingleStep(0.1)
        self.ui.velocity.setDecimals(2)
        self.ui.velocity.setSuffix(" mm/s")
        self.ui.velocity.setValue(self._applied_velocity)

    def setup_acceleration_selector(self):
        """Configura el selector de aceleración"""
        self.ui.acceleration.setFont(QFont("Sitka Small", 10))
        self.ui.acceleration.setMinimum(0.1)
        self.ui.acceleration.setMaximum(10000.0)
        self.ui.acceleration.setSingleStep(1.0)
        self.ui.acceleration.setDecimals(2)
        self.ui.acceleration.setSuffix(" mm/s²")
        self.ui.acceleration.setValue(self._applied_acceleration)

    # ─────────────────────────────────────────────────────────────────────
    # Compuerta de confirmación de Velocity/Acceleration (directriz 2.3)
    # ─────────────────────────────────────────────────────────────────────
    def _check_pending_changes(self):
        vel_pending = abs(self.ui.velocity.value() - self._applied_velocity) > 1e-9
        acc_pending = abs(self.ui.acceleration.value() - self._applied_acceleration) > 1e-9

        self.ui.velocity.setStyleSheet(PENDING_BORDER_STYLE if vel_pending else "")
        self.ui.acceleration.setStyleSheet(PENDING_BORDER_STYLE if acc_pending else "")
        self.ui.confirmBtn.setText("Aplicar cambios pendientes" if (vel_pending or acc_pending) else "Confirm")

    def confirm_values(self):
        """Aplica los valores de velocity/acceleration mostrados en pantalla y
        avisa al usuario (compuerta de confirmación real, ver 2.3)."""
        self._applied_velocity = self.ui.velocity.value()
        self._applied_acceleration = self.ui.acceleration.value()

        self.ui.velocity.setStyleSheet("")
        self.ui.acceleration.setStyleSheet("")
        self.ui.confirmBtn.setText("Confirm")

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Valores Guardados")
        msg.setText(f"Los valores han sido guardados correctamente:")
        msg.setInformativeText(f"Velocidad: {self._applied_velocity} mm/s\nAceleración: {self._applied_acceleration} mm/s²")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    # ─────────────────────────────────────────────────────────────────────
    # Control de potencia del láser — slider continuo (directriz 1.5 / 2.4)
    # ─────────────────────────────────────────────────────────────────────
    def setup_laser_power_section(self):
        """Configura el slider de potencia, el indicador de consigna y LÁSER OFF"""
        self.ui.laserPowerSlider.setMinimumWidth(160)

        self.ui.labelLaserPowerManual.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.labelLaserPowerManual.setToolTip(
            "Valor de consigna de potencia — no es una medida real, es el mando enviado al láser"
        )
        self.ui.labelLaserPowerManual.setMinimumWidth(120)
        self.ui.labelLaserPowerManual.setStyleSheet("""
            QLineEdit#labelLaserPowerManual {
                background-color: transparent;
                color: THEME.COLOR_TEXT_1;
                font-weight: bold;
                border: none;
            }
        """)
        self.ui.labelLaserPowerManual.setText("0% · 0 mW")

        self.ui.laserOffBtn.setFont(QFont("Sitka Small", 12, QFont.Weight.Bold))
        self.ui.laserOffBtn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: 2px solid #DA190B;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #DA190B;
            }
            QPushButton:pressed {
                background-color: #B71C1C;
            }
        """)

        # Estado inicial del icono laserOC en 0% (gris/apagado)
        self._apply_laser_icon_color(0)

    def handle_laser_power_changed(self, value):
        """Se dispara en vivo mientras se arrastra el slider (no solo al soltar)."""
        self.controller.set_laser_power_percent(value)
        _, duty_percent, power_mw = self.controller.get_laser_output_state()
        self.ui.labelLaserPowerManual.setText(f"{duty_percent:.0f}% · {power_mw:.0f} mW")
        self._apply_laser_icon_color(value)

    def _apply_laser_icon_color(self, percent):
        color = self._laser_color_for_percent(percent)
        self.ui.laserOC.setStyleSheet(f"""
            QLabel#laserOC {{
                background-color: {color};
                border-radius: 60%;
            }}
        """)

    def _laser_color_for_percent(self, percent):
        """Interpola linealmente de gris (0%, apagado) a rojo saturado (100%),
        pasando por un rojo tenue en valores bajos — sin saltos bruscos de color."""
        t = max(0.0, min(100.0, percent)) / 100.0
        gray = (0x80, 0x80, 0x80)
        red = (0xF4, 0x43, 0x36)
        r, g, b = (round(gray[i] + (red[i] - gray[i]) * t) for i in range(3))
        return f"#{r:02X}{g:02X}{b:02X}"
