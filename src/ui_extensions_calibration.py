########################################################################
## CALIBRATION PAGE EXTENSIONS
## Modificaciones de diseño para la página de calibración
########################################################################

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QFontMetrics, QIcon
from PySide6.QtWidgets import QSizePolicy, QMessageBox, QLabel, QVBoxLayout, QBoxLayout

import config
from src.aerotech_controller import AXIS_X, AXIS_Y, AXIS_Z

# Paso, velocidad y aceleración usados para el ajuste fino de enfoque en Z.
# No hay controles de escala/velocidad en esta página, así que se usan
# valores conservadores por defecto (ajustar según necesidad del laboratorio).
FOCUS_STEP_MM = 0.001        # 1 µm por pulsación
FOCUS_VELOCITY_MM_S = 0.5
FOCUS_ACCEL_MM_S2 = 5.0

# Eje al que está cableada la salida PSO del NEJE B30635 (ver
# 00_global_architecture.md — drive 1 / eje X).
PSO_AXIS = AXIS_X


class CalibrationPageExtensions:
    """Extensiones de UI para la página de calibración"""

    def __init__(self, ui, main_window, controller):
        self.ui = ui
        self.main = main_window
        # Instancia compartida de AerotechController (ver main.py)
        self.controller = controller

        # Master safety window (05_calibration.md §1.2): dos esquinas
        # capturadas por movimiento real (jog de Manual), no por texto.
        self._corner1 = None   # (x, y) mm
        self._corner2 = None   # (x, y) mm

        self._firing_alignment = False

    def apply_modifications(self):
        """Aplica todas las modificaciones de la página de calibración"""
        self.setup_title()
        self.setup_focusing_section()
        self.setup_calibration_xy_section()
        self.setup_safety_window_section()
        self.setup_alignment_mode_section()

    def connect_signals(self):
        """Conecta las señales específicas de la página de calibración"""
        # El resto de señales ya están conectadas en los setup_*() de arriba

        # Lectura de posición Z en vivo, ligera (no hay QTimer global para
        # páginas fuera de Home/Manual/Auto — GlobalStatusPanel solo se
        # muestra en esas tres).
        self.z_focus_timer = QTimer()
        self.z_focus_timer.timeout.connect(self.update_z_focus_display)
        self.z_focus_timer.start(100)

    def update_z_focus_display(self):
        if not self.controller.is_connected:
            self.ui.labelZFocusStatus.setText("Current Z: —")
            return
        _, _, z = self.controller.get_axis_positions()
        self.ui.labelZFocusStatus.setText(f"Current Z: {z:.3f} mm")

    @staticmethod
    def _fit_button_width(button, padding=24):
        """Ensancha el botón lo justo para que su texto (con la fuente ya
        aplicada) no se recorte por los lados — el ancho lo fijaba el
        contenedor padre sin comprobar si el texto cabía. Padding ajustado
        (antes 40) porque exigir el ancho de la frase completa en botones
        que van en pareja (Corner 1/Corner 2) desbordaba el ancho del panel
        lateral (08_ui_polish_fixes.md ronda 2, §3.3)."""
        text_width = QFontMetrics(button.font()).horizontalAdvance(button.text())
        button.setMinimumWidth(text_width + padding)

    @staticmethod
    def _enable_button_wrap(button, min_height, color_style=None):
        """QPushButton no tiene wordWrap nativo — en vez de forzar el ancho
        de la frase completa en una sola línea (lo que desbordaba el panel
        lateral), se superpone un QLabel interno con wordWrap activado y se
        vacía el texto propio del botón, para que el texto pueda partirse en
        2 líneas dentro del ancho que dé el layout padre."""
        if color_style is None:
            color_style = f"color: {config.THEME.COLOR_TEXT_1};"

        text = button.text()
        button.setText("")
        button.setMinimumHeight(min_height)

        label = QLabel(text, button)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(button.font())
        label.setAttribute(Qt.WA_TransparentForMouseEvents)
        label.setStyleSheet(f"background: transparent; {color_style}")

        layout = QVBoxLayout(button)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.addWidget(label)
        return label

    def setup_title(self):
        """Configura el título de la página"""
        self.ui.label_10.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.label_10.setStyleSheet(f"color: {config.THEME.COLOR_TEXT_1};")

    def setup_focusing_section(self):
        """Configura la sección de enfoque Z"""
        # Título de la sección
        self.ui.label_23.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.label_23.setStyleSheet(f"color: {config.THEME.COLOR_TEXT_1};")
        self.ui.label_23.setWordWrap(True)

        # Lectura de posición Z en vivo
        self.ui.labelZFocusStatus.setFont(QFont("Sitka Small", 10))
        self.ui.labelZFocusStatus.setStyleSheet(f"color: {config.THEME.COLOR_ACCENT_3};")
        self.ui.labelZFocusStatus.setText("Current Z: —")

        # Estilo común para botones de enfoque — mismos colores/hover que
        # Auto (setup_axis_control_section en ui_extensions_auto.py), para
        # que todos los botones de la aplicación se comporten igual.
        focus_button_style = f"""
            QPushButton {{
                background-color: {config.THEME.COLOR_BACKGROUND_2};
                color: {config.THEME.COLOR_TEXT_1};
                border: 2px solid {config.THEME.COLOR_ACCENT_3};
                border-radius: 5px;
                padding: 8px;
                min-height: 35px;
            }}
            QPushButton:hover {{
                background-color: {config.THEME.COLOR_ACCENT_2};
                color: white;
                border: 2px solid {config.THEME.COLOR_ACCENT_1};
            }}
            QPushButton:pressed {{
                background-color: {config.THEME.COLOR_ACCENT_1};
            }}
        """

        # Botón Z Up — altura mayor + wrap en 2 líneas (flecha arriba, texto
        # debajo). El QIcon propio del botón (icon26 en ui_interface.py) se
        # dibuja centrado en el botón en cuanto su texto queda vacío (lo hace
        # _enable_button_wrap) y terminaba solapado con la palabra "Up"/"Down"
        # del QLabel superpuesto — se quita el icono y la flecha pasa a ser la
        # primera línea del propio texto envuelto.
        self.ui.zUpFocusing.setIcon(QIcon())
        self.ui.zUpFocusing.setFont(QFont("Sitka Small", 10))
        self.ui.zUpFocusing.setStyleSheet(focus_button_style)
        self.ui.zUpFocusing.setText("▲\nMove Up")
        self._enable_button_wrap(self.ui.zUpFocusing, min_height=60)

        # Botón Z Down
        self.ui.zDownFocusing.setIcon(QIcon())
        self.ui.zDownFocusing.setFont(QFont("Sitka Small", 10))
        self.ui.zDownFocusing.setStyleSheet(focus_button_style)
        self.ui.zDownFocusing.setText("▼\nMove Down")
        self._enable_button_wrap(self.ui.zDownFocusing, min_height=60)

        # Botón "Confirm focus" — visualmente separado de subir/bajar (ya
        # está en su propia fila, debajo del par Up/Down). Pulsación manual
        # explícita del usuario tras ajustar Z a ojo — no se infiere de
        # ninguna lectura automática.
        self.ui.calibratedBtn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.calibratedBtn.setStyleSheet(f"""
            QPushButton {{
                background-color: {config.THEME.COLOR_BACKGROUND_2};
                color: {config.THEME.COLOR_TEXT_1};
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 10px;
                min-height: 40px;
                margin-top: 10px;
            }}
            QPushButton:hover {{
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
            }}
            QPushButton:pressed {{
                background-color: #45a049;
            }}
        """)
        self.ui.calibratedBtn.setText("Confirm focus")
        self._calibratedBtn_label = self._enable_button_wrap(self.ui.calibratedBtn, min_height=55)

        # Conectar señales
        self.ui.zUpFocusing.clicked.connect(self.handle_z_up_focusing)
        self.ui.zDownFocusing.clicked.connect(self.handle_z_down_focusing)
        self.ui.calibratedBtn.clicked.connect(self.confirm_focus)

    def setup_calibration_xy_section(self):
        """Configura la sección de calibración X-Y"""
        # Título de la sección
        self.ui.label_24.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.label_24.setStyleSheet(f"color: {config.THEME.COLOR_TEXT_1};")
        self.ui.label_24.setWordWrap(True)
        # El label tenía política de altura vertical Fixed (fijada en Qt
        # Designer sobre el sizeHint de una sola línea, antes de activar
        # wordWrap aquí) — al envolver a 2 líneas, el contenido no cabía en
        # esa altura fija y las líneas se dibujaban superpuestas. Con
        # Preferred, el layout recalcula la altura según el contenido.
        label_24_policy = self.ui.label_24.sizePolicy()
        label_24_policy.setVerticalPolicy(QSizePolicy.Policy.Preferred)
        self.ui.label_24.setSizePolicy(label_24_policy)

        # Estilo común para botones de calibración — mismos colores/hover
        # que Auto, en vez de la variante naranja propia de esta página.
        calibration_button_style = f"""
            QPushButton {{
                background-color: {config.THEME.COLOR_BACKGROUND_2};
                color: {config.THEME.COLOR_TEXT_1};
                border: 2px solid {config.THEME.COLOR_ACCENT_3};
                border-radius: 8px;
                padding: 10px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {config.THEME.COLOR_ACCENT_2};
                color: white;
                border: 2px solid {config.THEME.COLOR_ACCENT_1};
            }}
            QPushButton:pressed {{
                background-color: {config.THEME.COLOR_ACCENT_1};
            }}
        """

        # Botón Zero X
        self.ui.zeroXBtn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.zeroXBtn.setStyleSheet(calibration_button_style)
        self.ui.zeroXBtn.setText("Zero X Position")
        self._zeroXBtn_label = self._enable_button_wrap(self.ui.zeroXBtn, min_height=50)

        # Botón Zero Y
        self.ui.zeroYBtn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.zeroYBtn.setStyleSheet(calibration_button_style)
        self.ui.zeroYBtn.setText("Zero Y Position")
        self._zeroYBtn_label = self._enable_button_wrap(self.ui.zeroYBtn, min_height=50)

        # Conectar señales
        self.ui.zeroXBtn.clicked.connect(self.handle_zero_x)
        self.ui.zeroYBtn.clicked.connect(self.handle_zero_y)

    # ─────────────────────────────────────────────────────────────────────
    # Master safety window (directriz 1.2 / 2.1 de 05_calibration.md)
    # ─────────────────────────────────────────────────────────────────────
    def setup_safety_window_section(self):
        self.ui.label_safetyWindowTitle.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.label_safetyWindowTitle.setStyleSheet(f"color: {config.THEME.COLOR_TEXT_1};")
        # "Master Safety Window" se recortaba por el borde derecho del panel
        # en vez de ajustar línea — provocaba scroll horizontal en toda la
        # página (08_ui_polish_fixes.md ronda 2, §3.3)
        self.ui.label_safetyWindowTitle.setWordWrap(True)

        for label in (self.ui.label_xMinField, self.ui.label_xMaxField,
                      self.ui.label_yMinField, self.ui.label_yMaxField):
            label.setFont(QFont("Sitka Small", 9))
            label.setStyleSheet(f"color: {config.THEME.COLOR_TEXT_1};")

        for field in (self.ui.xMinField, self.ui.xMaxField, self.ui.yMinField, self.ui.yMaxField):
            field.setFont(QFont("Sitka Small", 9, QFont.Weight.Bold))
            field.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {config.THEME.COLOR_BACKGROUND_2};
                    color: {config.THEME.COLOR_TEXT_1};
                    border: 2px solid {config.THEME.COLOR_ACCENT_3};
                    border-radius: 5px;
                }}
            """)

        # Mismo estilo que "Confirm focus" (calibratedBtn en
        # setup_focusing_section) — no un estilo nuevo para estos dos.
        corner_button_style = f"""
            QPushButton {{
                background-color: {config.THEME.COLOR_BACKGROUND_2};
                color: {config.THEME.COLOR_TEXT_1};
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 10px;
                min-height: 50px;
                margin-top: 10px;
            }}
            QPushButton:hover {{
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
            }}
            QPushButton:pressed {{
                background-color: #45a049;
            }}
        """
        # Apilados verticalmente (antes en horizontal, uno al lado del otro,
        # competían por ancho en el panel lateral estrecho y "Corner 1"/
        # "Corner 2" se recortaban pese al ancho mínimo fijo ya probado en
        # 11_style_unification.md) — mismo QHBoxLayout ya definido en
        # ui_interface.py, solo se le cambia la dirección, así cada botón usa
        # todo el ancho disponible del panel.
        self.ui.horizontalLayout_safetyWindowButtons.setDirection(QBoxLayout.Direction.TopToBottom)

        self.ui.setCorner1Btn.setText("Corner 1")
        self.ui.setCorner1Btn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.setCorner1Btn.setStyleSheet(corner_button_style)
        self.ui.setCorner2Btn.setText("Corner 2")
        self.ui.setCorner2Btn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.setCorner2Btn.setStyleSheet(corner_button_style)

        self.ui.setCorner1Btn.clicked.connect(self.capture_corner_1)
        self.ui.setCorner2Btn.clicked.connect(self.capture_corner_2)

    def capture_corner_1(self):
        """Captura la posición X/Y actual como primera esquina de la ventana
        maestra (mover primero con el jog de Manual hasta la esquina real)."""
        if not self._confirm_redefine_if_needed():
            return
        x, y, _ = self.controller.get_axis_positions()
        self._corner1 = (x, y)
        print(f"[Calibration] Corner 1 set at X={x:.3f} Y={y:.3f}")
        self._recompute_safety_window()

    def capture_corner_2(self):
        """Captura la posición X/Y actual como segunda esquina de la ventana
        maestra."""
        if not self._confirm_redefine_if_needed():
            return
        x, y, _ = self.controller.get_axis_positions()
        self._corner2 = (x, y)
        print(f"[Calibration] Corner 2 set at X={x:.3f} Y={y:.3f}")
        self._recompute_safety_window()

    def _confirm_redefine_if_needed(self):
        """Redefinir una ventana ya calibrada (las dos esquinas ya
        capturadas) exige confirmación explícita del usuario."""
        if self._corner1 is None or self._corner2 is None:
            return True
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Redefine safety window?")
        msg.setText("The safety window is already calibrated. Redefining a corner will change it.")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        return msg.exec() == QMessageBox.StandardButton.Yes

    def _recompute_safety_window(self):
        if self._corner1 is None or self._corner2 is None:
            return
        window = self.get_safety_window()
        self.ui.xMinField.setText(f"{window['x_min']:.3f}")
        self.ui.xMaxField.setText(f"{window['x_max']:.3f}")
        self.ui.yMinField.setText(f"{window['y_min']:.3f}")
        self.ui.yMaxField.setText(f"{window['y_max']:.3f}")

    def get_safety_window(self):
        """
        Expone la ventana maestra de posición a Auto y G-Code (M901).
        Devuelve {"x_min", "x_max", "y_min", "y_max"} o None si todavía no
        se han capturado las dos esquinas.
        """
        if self._corner1 is None or self._corner2 is None:
            return None
        x1, y1 = self._corner1
        x2, y2 = self._corner2
        return {
            "x_min": min(x1, x2), "x_max": max(x1, x2),
            "y_min": min(y1, y2), "y_max": max(y1, y2),
        }

    # ─────────────────────────────────────────────────────────────────────
    # Laser alignment mode (directriz 1.3 / 2.1 de 05_calibration.md)
    # ─────────────────────────────────────────────────────────────────────
    def setup_alignment_mode_section(self):
        # "Laser alignment mode" se recortaba por los bordes — etiqueta
        # acortada a "Alignment mode"
        self.ui.alignmentModeToggle.setText("Alignment mode")
        self.ui.alignmentModeToggle.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.alignmentModeToggle.setMinimumHeight(40)
        self._fit_button_width(self.ui.alignmentModeToggle)
        self.ui.alignmentModeToggle.setStyleSheet(f"""
            QPushButton {{
                background-color: {config.THEME.COLOR_BACKGROUND_2};
                color: {config.THEME.COLOR_TEXT_1};
                border: 2px solid {config.THEME.COLOR_ACCENT_3};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {config.THEME.COLOR_ACCENT_2};
                color: white;
                border: 2px solid {config.THEME.COLOR_ACCENT_1};
            }}
            QPushButton:checked {{
                background-color: #FFA726;
                color: white;
                border: 2px solid #FB8C00;
            }}
        """)

        # El tope de potencia (config.ALIGNMENT_MODE_MAX_POWER_PERCENT) se
        # sigue aplicando igual en _start_alignment_firing(); label_alignmentPower
        # solo anunciaba el número en pantalla, ya no se muestra.
        self.ui.label_alignmentPower.setText("")
        self.ui.label_alignmentPower.hide()

        # Mismo tamaño/estilo que "Laser ON" (laserFireBtn) en Manual, sin
        # ninguna regla añadida — ver setup_laser_power_section() en
        # ui_extensions_manual.py. Un ":disabled" con color propio (probado
        # antes) dejaba el contorno en azul mientras no se activa Alignment
        # mode; Qt ya atenúa un QPushButton deshabilitado por su cuenta sin
        # necesidad de una regla QSS aparte, así que se quita del todo.
        self.ui.alignmentFireBtn.setFont(QFont("Sitka Small", 12, QFont.Weight.Bold))
        self.ui.alignmentFireBtn.setMinimumSize(150, 60)
        self.ui.alignmentFireBtn.setEnabled(False)
        self.ui.alignmentFireBtn.setStyleSheet("""
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

        self.ui.alignmentModeToggle.clicked.connect(self.handle_alignment_mode_toggle)
        self.ui.alignmentFireBtn.pressed.connect(self._start_alignment_firing)
        self.ui.alignmentFireBtn.released.connect(self._stop_alignment_firing)

    def handle_alignment_mode_toggle(self):
        active = self.ui.alignmentModeToggle.isChecked()
        self.ui.alignmentFireBtn.setEnabled(active)
        if not active:
            # Al desactivarse, fuerza pso_output_off (directriz 2.1)
            self.controller.pso_output_off(PSO_AXIS)
            self._firing_alignment = False

    def _start_alignment_firing(self):
        if not self.ui.alignmentModeToggle.isChecked():
            return
        self._firing_alignment = True
        self.controller.pso_configure_waveform(PSO_AXIS, config.ALIGNMENT_MODE_MAX_POWER_PERCENT)
        self.controller.pso_output_on(PSO_AXIS)

    def _stop_alignment_firing(self):
        self._firing_alignment = False
        self.controller.pso_output_off(PSO_AXIS)

    # ─────────────────────────────────────────────────────────────────────
    # Enfoque Z / Zero X / Zero Y
    # ─────────────────────────────────────────────────────────────────────
    def handle_z_up_focusing(self):
        """Maneja el movimiento Z hacia arriba para enfoque"""
        print("Calibration: Moving Z up for focusing...")
        self.controller.move_relative(AXIS_Z, FOCUS_STEP_MM, FOCUS_VELOCITY_MM_S, FOCUS_ACCEL_MM_S2)

    def handle_z_down_focusing(self):
        """Maneja el movimiento Z hacia abajo para enfoque"""
        print("Calibration: Moving Z down for focusing...")
        self.controller.move_relative(AXIS_Z, -FOCUS_STEP_MM, FOCUS_VELOCITY_MM_S, FOCUS_ACCEL_MM_S2)

    def confirm_focus(self):
        """
        Confirma manualmente el enfoque Z tras ajustarlo a ojo (con Move
        Up/Down o con el jog de Manual). Reutiliza zero_axis(Z, ...), el
        mismo mecanismo que ya usaba el antiguo calibratedBtn — no se crea
        una función paralela.
        """
        print("Calibration: Z position confirmed as focus (zeroed)")
        self.controller.zero_axis(AXIS_Z)

        # Feedback visual — el texto vive en el QLabel interno (wrap
        # activado por _enable_button_wrap), no en el propio QPushButton
        self._calibratedBtn_label.setText("✓ Focus confirmed!")
        self._calibratedBtn_label.setStyleSheet("background: transparent; color: white;")
        self.ui.calibratedBtn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
                border-radius: 8px;
                padding: 10px;
                min-height: 55px;
                font-weight: bold;
                margin-top: 10px;
            }
        """)

    def handle_zero_x(self):
        """Maneja la configuración de X = 0"""
        print("Calibration: Setting X position to zero")
        self.controller.zero_axis(AXIS_X)

        # Feedback visual — el texto vive en el QLabel interno
        self._zeroXBtn_label.setText("✓ X = 0 Set")
        self._zeroXBtn_label.setStyleSheet("background: transparent; color: white;")
        self.ui.zeroXBtn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
                border-radius: 8px;
                padding: 10px;
                min-height: 50px;
                font-weight: bold;
            }
        """)

    def handle_zero_y(self):
        """Maneja la configuración de Y = 0"""
        print("Calibration: Setting Y position to zero")
        self.controller.zero_axis(AXIS_Y)

        # Feedback visual — el texto vive en el QLabel interno
        self._zeroYBtn_label.setText("✓ Y = 0 Set")
        self._zeroYBtn_label.setStyleSheet("background: transparent; color: white;")
        self.ui.zeroYBtn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
                border-radius: 8px;
                padding: 10px;
                min-height: 50px;
                font-weight: bold;
            }
        """)
