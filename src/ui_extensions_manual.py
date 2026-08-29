########################################################################
## MANUAL PAGE EXTENSIONS
########################################################################

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMessageBox

import config
from src.aerotech_controller import AXIS_X, AXIS_Y, AXIS_Z, NEJE_B30635_MAX_POWER_MW

AXIS_CONST = {"X": AXIS_X, "Y": AXIS_Y, "Z": AXIS_Z}

# Borde naranja para Velocity mientras el valor en pantalla no coincide con
# el valor realmente aplicado a los movimientos (ver 02_manual.md §2.2).
PENDING_BORDER_STYLE = "QDoubleSpinBox { border: 2px solid #FFA726; }"


class ManualPageExtensions:
    """
    Extensiones de UI para la página Manual Mode.

    Tras la migración a GlobalStatusPanel (agosto de 2026, ver
    00_global_architecture.md), Manual ya no tiene su propia copia de
    posición/LEDs por eje (vivían en positionManual/ledRowManual<Axis>) — el
    panel compartido de main.py ya cubre eso. axisControlManual se mantiene:
    son controles activos (Enable/Disable/Home), no un indicador pasivo.

    El control de aceleración desapareció de la interfaz (02_manual.md §1.3):
    solo queda velocity, con la misma compuerta de confirmación; la
    aceleración usa config.DEFAULT_ACCELERATION_MM_S2[axis], fija.

    El láser pasó de "en vivo" a "mantener pulsado" sobre PSO real
    (02_manual.md §1.4/2.3): laserPowerSlider ya solo fija una consigna,
    laserFireBtn dispara mientras se mantiene pulsado.
    """

    def __init__(self, ui, main_window, controller):
        self.ui = ui
        self.main = main_window
        # Instancia compartida de AerotechController (ver main.py)
        self.controller = controller

        # Valor de velocidad realmente aplicado a los movimientos — distinto
        # de lo que muestre el spinbox mientras haya un cambio sin confirmar.
        self._applied_velocity = 10.0

        # Eje que dispara el láser (fijo: NEJE cableado a la salida PSO del
        # drive 1 / eje X, ver 00_global_architecture.md §3).
        self._laser_axis = AXIS_X
        self._firing = False

        # Relé que alimenta la placa adaptadora del NEJE (Digital Output
        # [-EB1] Output 1, ver 07_laser_hardware_integration.md) — apagado
        # por defecto al arrancar.
        self._board_power = False

    def apply_modifications(self):
        """Aplica todas las modificaciones de la página Manual"""
        self.setup_axis_control_section()
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

        # Compuerta de confirmación de velocity
        self.ui.confirmBtn.clicked.connect(self.confirm_values)
        self.ui.velocity.valueChanged.connect(self._check_pending_changes)

        # Control por eje: enable/disable + home
        self.ui.toggleXBtn.clicked.connect(lambda: self.handle_toggle_axis("X"))
        self.ui.toggleYBtn.clicked.connect(lambda: self.handle_toggle_axis("Y"))
        self.ui.toggleZBtn.clicked.connect(lambda: self.handle_toggle_axis("Z"))
        self.ui.homeXBtn.clicked.connect(lambda: self.controller.home_axes([AXIS_X]))
        self.ui.homeYBtn.clicked.connect(lambda: self.controller.home_axes([AXIS_Y]))
        self.ui.homeZBtn.clicked.connect(lambda: self.controller.home_axes([AXIS_Z]))

        # Consigna de potencia del láser (solo fija el valor mostrado/color;
        # NO dispara nada por sí sola — ver 02_manual.md §1.4)
        self.ui.laserPowerSlider.valueChanged.connect(self.handle_laser_power_changed)

        # Relé de alimentación de la placa adaptadora del NEJE (ver
        # 07_laser_hardware_integration.md §2)
        self.ui.laserBoardPowerBtn.toggled.connect(self.handle_laser_board_power_toggled)

        # Disparo por mantener pulsado, sobre PSO real
        self.ui.laserFireBtn.pressed.connect(self._start_firing)
        self.ui.laserFireBtn.released.connect(self._stop_firing)

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
        acceleration = config.DEFAULT_ACCELERATION_MM_S2[AXIS_X]

        print(f"Moving X+ | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_X, scale, velocity, acceleration)

    def move_x_negative(self):
        """Mueve X en dirección negativa"""
        scale = self.get_current_scale()
        velocity = self._applied_velocity
        acceleration = config.DEFAULT_ACCELERATION_MM_S2[AXIS_X]

        print(f"Moving X- | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_X, -scale, velocity, acceleration)

    def move_y_positive(self):
        """Mueve Y en dirección positiva"""
        scale = self.get_current_scale()
        velocity = self._applied_velocity
        acceleration = config.DEFAULT_ACCELERATION_MM_S2[AXIS_Y]

        print(f"Moving Y+ | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_Y, scale, velocity, acceleration)

    def move_y_negative(self):
        """Mueve Y en dirección negativa"""
        scale = self.get_current_scale()
        velocity = self._applied_velocity
        acceleration = config.DEFAULT_ACCELERATION_MM_S2[AXIS_Y]

        print(f"Moving Y- | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_Y, -scale, velocity, acceleration)

    def move_z_positive(self):
        """Mueve Z en dirección positiva"""
        scale = self.get_current_scale()
        velocity = self._applied_velocity
        acceleration = config.DEFAULT_ACCELERATION_MM_S2[AXIS_Z]

        print(f"Moving Z+ | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_Z, scale, velocity, acceleration)

    def move_z_negative(self):
        """Mueve Z en dirección negativa"""
        scale = self.get_current_scale()
        velocity = self._applied_velocity
        acceleration = config.DEFAULT_ACCELERATION_MM_S2[AXIS_Z]

        print(f"Moving Z- | Scale: {scale} | Vel: {velocity} | Acc: {acceleration}")
        self._move_relative(AXIS_Z, -scale, velocity, acceleration)

    def move_xy_zero(self):
        """Mueve XY a posición cero"""
        velocity = self._applied_velocity
        acceleration = config.DEFAULT_ACCELERATION_MM_S2[AXIS_X]

        print(f"Moving to XY Zero | Vel: {velocity} | Acc: {acceleration}")
        self.controller.move_absolute([AXIS_X, AXIS_Y], [0.0, 0.0], velocity, acceleration)

    # ─────────────────────────────────────────────────────────────────────
    # Control por eje: Enable/Disable + Home
    # ─────────────────────────────────────────────────────────────────────
    def handle_toggle_axis(self, axis):
        """Alterna habilitación/deshabilitación de un único eje (patrón de
        connectBtn). El botón mantiene siempre el texto "Enable" — el
        estado enabled/disabled ya lo indica el color vía QPushButton:checked
        (ver toggle_style en setup_axis_control_section)."""
        btn = {"X": self.ui.toggleXBtn, "Y": self.ui.toggleYBtn, "Z": self.ui.toggleZBtn}[axis]
        axis_const = AXIS_CONST[axis]
        if btn.isChecked():
            self.controller.enable_axes([axis_const])
        else:
            self.controller.disable_axes([axis_const])

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
        """Configura los 3 bloques de control por eje (Enable/Disable, Home)"""
        axis_specs = [
            (self.ui.labelAxisX, self.ui.toggleXBtn, self.ui.homeXBtn),
            (self.ui.labelAxisY, self.ui.toggleYBtn, self.ui.homeYBtn),
            (self.ui.labelAxisZ, self.ui.toggleZBtn, self.ui.homeZBtn),
        ]

        toggle_style = f"""
            QPushButton {{
                background-color: {THEME.COLOR_BACKGROUND_2};
                color: {THEME.COLOR_TEXT_1};
                border: 2px solid {THEME.COLOR_ACCENT_3};
                border-radius: 8px;
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: {THEME.COLOR_ACCENT_2};
                color: white;
                border: 2px solid {THEME.COLOR_ACCENT_1};
            }}
            QPushButton:checked {{
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
            }}
        """
        home_style = f"""
            QPushButton {{
                background-color: {THEME.COLOR_BACKGROUND_2};
                color: {THEME.COLOR_TEXT_1};
                border: 2px solid {THEME.COLOR_ACCENT_3};
                border-radius: 8px;
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: {THEME.COLOR_ACCENT_1};
                color: white;
            }}
        """

        for label, toggle_btn, home_btn in axis_specs:
            label.setFont(QFont("Sitka Small", 13, QFont.Weight.Bold))
            label.setStyleSheet(f"color: {THEME.COLOR_TEXT_1};")

            toggle_btn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
            toggle_btn.setMinimumHeight(40)
            toggle_btn.setStyleSheet(toggle_style)
            toggle_btn.setText("Enable")

            home_btn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
            home_btn.setMinimumHeight(36)
            home_btn.setStyleSheet(home_style)

    def setup_movement_section(self):
        """Configura la sección de movimiento XYZ"""
        # Título de Moviviento XYZ
        self.ui.label_19.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.label_19.setStyleSheet(f"color: {THEME.COLOR_TEXT_1};")

        # Configurar selector de escala y velocidad (ya no hay aceleración)
        self.ui.label_31.setFont(QFont("Sitka Small", 10))
        self.setup_scale_selector()
        self.ui.label_32.setFont(QFont("Sitka Small", 10))
        self.setup_velocity_selector()

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

        # Multiplicador ×N
        self.ui.scaleMultiplier.setFont(QFont("Sitka Small", 10))
        self.ui.scaleMultiplier.setToolTip("Jog step multiplier (scale × N)")

    def setup_velocity_selector(self):
        """Configura el selector de velocidad"""
        self.ui.velocity.setFont(QFont("Sitka Small", 10))
        self.ui.velocity.setMinimum(0.1)
        self.ui.velocity.setMaximum(1000.0)
        self.ui.velocity.setSingleStep(0.1)
        self.ui.velocity.setDecimals(2)
        self.ui.velocity.setSuffix(" mm/s")
        self.ui.velocity.setValue(self._applied_velocity)

    # ─────────────────────────────────────────────────────────────────────
    # Compuerta de confirmación de Velocity
    # ─────────────────────────────────────────────────────────────────────
    def _check_pending_changes(self):
        vel_pending = abs(self.ui.velocity.value() - self._applied_velocity) > 1e-9

        self.ui.velocity.setStyleSheet(PENDING_BORDER_STYLE if vel_pending else "")
        self.ui.confirmBtn.setText("Apply pending changes" if vel_pending else "Confirm")

    def confirm_values(self):
        """Aplica el valor de velocity mostrado en pantalla y avisa al usuario
        (compuerta de confirmación real)."""
        self._applied_velocity = self.ui.velocity.value()

        self.ui.velocity.setStyleSheet("")
        self.ui.confirmBtn.setText("Confirm")

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Values Saved")
        msg.setText("Values have been saved successfully:")
        msg.setInformativeText(f"Velocity: {self._applied_velocity} mm/s")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    # ─────────────────────────────────────────────────────────────────────
    # Control de potencia del láser — mantener pulsado, sobre PSO real
    # ─────────────────────────────────────────────────────────────────────
    def setup_laser_power_section(self):
        """Configura el slider de consigna, el indicador y el botón de disparo"""
        self.ui.laserBoardPowerBtn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.laserBoardPowerBtn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME.COLOR_BACKGROUND_2};
                color: {THEME.COLOR_TEXT_1};
                border: 2px solid {THEME.COLOR_ACCENT_3};
                border-radius: 8px;
                padding: 6px;
            }}
            QPushButton:checked {{
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
            }}
        """)
        self.ui.laserBoardPowerBtn.setChecked(False)
        self.ui.laserBoardPowerBtn.setText("Laser board power: OFF")

        self.ui.laserPowerSlider.setMinimumWidth(160)

        self.ui.labelLaserPowerManual.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.labelLaserPowerManual.setToolTip(
            "Power setpoint — not a real measurement, this is the command sent to the laser"
        )
        self.ui.labelLaserPowerManual.setMinimumWidth(120)
        self.ui.labelLaserPowerManual.setStyleSheet(f"""
            QLineEdit#labelLaserPowerManual {{
                background-color: transparent;
                color: {THEME.COLOR_TEXT_1};
                font-weight: bold;
                border: none;
            }}
        """)
        self.ui.labelLaserPowerManual.setText("0% · 0 mW")

        self.ui.laserFireBtn.setFont(QFont("Sitka Small", 12, QFont.Weight.Bold))
        self.ui.laserFireBtn.setText("Laser ON")
        self.ui.laserFireBtn.setStyleSheet("""
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
        """
        Solo fija la consigna mostrada y el color de laserOC — ya NO llama a
        set_laser_power_percent() ni dispara nada por sí solo (a diferencia
        del comportamiento anterior). El disparo real ocurre en
        _start_firing()/_stop_firing(), vía PSO.
        """
        power_mw = value / 100 * NEJE_B30635_MAX_POWER_MW
        self.ui.labelLaserPowerManual.setText(f"{value:.0f}% · {power_mw:.0f} mW")
        self._apply_laser_icon_color(value if (self._firing and self._board_power) else 0)

    def handle_laser_board_power_toggled(self, checked):
        """laserBoardPowerBtn.toggled — abre/cierra el relé que alimenta la
        placa adaptadora del NEJE (ver 07_laser_hardware_integration.md §2)."""
        self._board_power = checked
        self.controller.set_laser_board_power(checked)
        self.ui.laserBoardPowerBtn.setText(f"Laser board power: {'ON' if checked else 'OFF'}")
        # Si el relé se abre mientras se mantenía pulsado el disparo, laserOC
        # no debe seguir sugiriendo que hay emisión real.
        if not checked:
            self._apply_laser_icon_color(0)
        elif self._firing:
            self._apply_laser_icon_color(self.ui.laserPowerSlider.value())

    def _start_firing(self):
        """laserFireBtn.pressed — dispara mientras se mantiene pulsado.
        fire_laser() garantiza que el relé quede cerrado, así que el toggle
        laserBoardPowerBtn se sincroniza con ese estado real (si estaba
        apagado, pasa a encendido) en vez de dejar la interfaz mintiendo
        sobre si hay alimentación real en la placa."""
        power_percent = self.ui.laserPowerSlider.value()
        self._firing = True
        self.controller.fire_laser(power_percent)
        if not self.ui.laserBoardPowerBtn.isChecked():
            self.ui.laserBoardPowerBtn.setChecked(True)
        self._apply_laser_icon_color(power_percent)

    def _stop_firing(self):
        """laserFireBtn.released — corta el disparo por PSO, sin abrir el
        relé (eso es acción explícita del toggle laserBoardPowerBtn o de
        'Laser stop')."""
        self._firing = False
        self.controller.stop_laser(cut_power=False)
        self._apply_laser_icon_color(0)

    def handle_emergency_stop(self):
        """Conectado a GlobalStatusPanel.laser_emergency_stop (ver main.py):
        pone la consigna a 0 y corta el disparo si estaba en curso."""
        self.ui.laserPowerSlider.setValue(0)
        if self._firing:
            self._stop_firing()

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
