########################################################################
## AUTO PAGE EXTENSIONS
########################################################################

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy, QMessageBox

from src.aerotech_controller import AXIS_X, AXIS_Y, AXIS_Z

# Salida digital que controla el shutter del láser en la página Auto.
# Debe coincidir con la usada en ui_extensions_manual.py (mismo shutter físico).
SHUTTER_OUTPUT_AXIS = AXIS_X
SHUTTER_OUTPUT_NUM = 0


class AutoPageExtensions:
    """Extensiones de UI para la página Auto Mode"""

    def __init__(self, ui, main_window, controller):
        self.ui = ui
        self.main = main_window
        self._saved_shutter_time_s = 1.0
        # Instancia compartida de AerotechController (ver src/ui_extensions.py)
        self.controller = controller

    def apply_modifications(self):
        """Aplica todas las modificaciones de la página Auto"""
        self.setup_movement_section()
        self.setup_shutter_section()

    def connect_signals(self):
        """Conecta las señales específicas de la página Auto"""
        # Sincronización scaleList_2 ↔ scaleList (Manual) 
        self.ui.scaleList_2.currentIndexChanged.connect(self._on_auto_scale_changed)
        self.ui.scaleList.currentIndexChanged.connect(self._on_manual_scale_changed)

        # Sincronización velocity_2 ↔ velocity (Manual)
        self.ui.velocity_2.valueChanged.connect(self._on_auto_velocity_changed)
        self.ui.velocity.valueChanged.connect(self._on_manual_velocity_changed)

        # Sincronización acceleration_2 ↔ acceleration (Manual)
        self.ui.acceleration_2.valueChanged.connect(self._on_auto_acceleration_changed)
        self.ui.acceleration.valueChanged.connect(self._on_manual_acceleration_changed)

        # Sincronización confirmBtn_2 ↔ confirmBtn (Manual)
        self.ui.confirmBtn_2.clicked.connect(self._confirm_values_auto)
        self.ui.confirmBtn.clicked.connect(self._confirm_values_manual)

        # Posición absoluta 
        self.ui.moveBtn.clicked.connect(self.handle_move_to_position)
        self.ui.resetBtn.clicked.connect(self.handle_reset_position)

        # Tiempo shutter
        self.ui.scaleListTime.currentIndexChanged.connect(self._on_time_scale_changed)
        self.ui.acceptBtn.clicked.connect(self.handle_accept_shutter_time)

    # ─────────────────────────────────────────────────────────────────────
    # Sincronización de los cuadros de lista 
    # ─────────────────────────────────────────────────────────────────────
    # Escala 
    def _on_auto_scale_changed(self, index):
        """Auto → Manual: propaga el índice de escala sin bucle"""
        self.ui.scaleList.blockSignals(True)
        self.ui.scaleList.setCurrentIndex(index)
        self.ui.scaleList.blockSignals(False)

    def _on_manual_scale_changed(self, index):
        """Manual → Auto: propaga el índice de escala sin bucle"""
        self.ui.scaleList_2.blockSignals(True)
        self.ui.scaleList_2.setCurrentIndex(index)
        self.ui.scaleList_2.blockSignals(False)

    # Velocidad 
    def _on_auto_velocity_changed(self, value):
        """Auto → Manual: propaga el valor de velocidad sin bucle"""
        self.ui.velocity.blockSignals(True)
        self.ui.velocity.setValue(value)
        self.ui.velocity.blockSignals(False)

    def _on_manual_velocity_changed(self, value):
        """Manual → Auto: propaga el valor de velocidad sin bucle"""
        self.ui.velocity_2.blockSignals(True)
        self.ui.velocity_2.setValue(value)
        self.ui.velocity_2.blockSignals(False)

    # Aceleración 
    def _on_auto_acceleration_changed(self, value):
        """Auto → Manual: propaga el valor de aceleración sin bucle"""
        self.ui.acceleration.blockSignals(True)
        self.ui.acceleration.setValue(value)
        self.ui.acceleration.blockSignals(False)

    def _on_manual_acceleration_changed(self, value):
        """Manual → Auto: propaga el valor de aceleración sin bucle"""
        self.ui.acceleration_2.blockSignals(True)
        self.ui.acceleration_2.setValue(value)
        self.ui.acceleration_2.blockSignals(False)

    # Confirm (mismo comportamiento en ambas páginas) 
    def _confirm_values_auto(self):
        """Confirma y muestra los valores de la página Auto"""
        velocity = self.ui.velocity_2.value()
        acceleration = self.ui.acceleration_2.value()
        self._show_confirm_dialog(velocity, acceleration)

    def _confirm_values_manual(self):
        """Confirma y muestra los valores de la página Manual"""
        velocity = self.ui.velocity.value()
        acceleration = self.ui.acceleration.value()
        self._show_confirm_dialog(velocity, acceleration)

    def _show_confirm_dialog(self, velocity, acceleration):
        """Muestra el mensaje de confirmación de velocidad/aceleración"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Valores Guardados")
        msg.setText("Los valores han sido guardados correctamente:")
        msg.setInformativeText(
            f"Velocidad: {velocity} mm/s\nAceleración: {acceleration} mm/s²"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    # =====================================================================
    # SECCIÓN DE MOVIMIENTO 
    # =====================================================================
    # ─────────────────────────────────────────────────────────────────────
    # Modificación de la interfaz de usuario
    # ───────────────────────────────────────────────────────────────────── 
    def setup_movement_section(self):
        """Configura la sección de movimiento XYZ absoluto"""
        # Título principal
        self.ui.label_15.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.label_15.setStyleSheet("color: THEME.COLOR_TEXT_1;")

        # Subtítulo "Absolute Motion"
        self.ui.label_13.setFont(QFont("Sitka Small", 10))
        self.ui.label_13.setStyleSheet("color: THEME.COLOR_ACCENT_1;")

        # Labels de posición
        position_labels = [
            (self.ui.label_17, "X Position"),
            (self.ui.label_25, "Y Position"),
            (self.ui.label_26, "Z Position"),
        ]
        for label, text in position_labels:
            label.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
            label.setText(text)
            label.setStyleSheet("color: THEME.COLOR_TEXT_1;")

        # SpinBoxes de posición absoluta
        self._setup_position_spinbox(self.ui.xPosition)
        self._setup_position_spinbox(self.ui.yPosition)
        self._setup_position_spinbox(self.ui.zPosition)

        # Botones moveBtn y resetBtn
        self._setup_move_reset_buttons()

        # Sección de escala / velocidad / aceleración (espejo de Manual)
        self._setup_scale_selector_auto()
        self._setup_velocity_selector_auto()
        self._setup_acceleration_selector_auto()

        # Labels de escala/vel/acc en la página Auto
        for label in (self.ui.label_38, self.ui.label_40, self.ui.label_39):
            label.setFont(QFont("Sitka Small", 10))
            label.setStyleSheet("color: THEME.COLOR_TEXT_1;")

    def _setup_position_spinbox(self, spinbox):
        """Configura un QDoubleSpinBox de posición absoluta"""
        spinbox.setFont(QFont("Sitka Small", 10))
        spinbox.setMinimum(-1000.0)
        spinbox.setMaximum(1000.0)
        spinbox.setSingleStep(0.1)
        spinbox.setDecimals(3)
        spinbox.setSuffix(" mm")
        spinbox.setValue(0.0)
        spinbox.setMinimumWidth(120)
        spinbox.setStyleSheet("""
            QDoubleSpinBox {
                background-color: THEME.COLOR_BACKGROUND_2;
                color: THEME.COLOR_TEXT_1;
                border: 2px solid THEME.COLOR_ACCENT_3;
                border-radius: 8px;
                padding: 6px;
                font-weight: bold;
            }
            QDoubleSpinBox:hover {
                border: 2px solid THEME.COLOR_ACCENT_1;
            }
            QDoubleSpinBox:focus {
                border: 2px solid THEME.COLOR_ACCENT_1;
                background-color: THEME.COLOR_BACKGROUND_3;
            }
        """)

    def _setup_move_reset_buttons(self):
        """Configura moveBtn y resetBtn"""
        for btn in (self.ui.moveBtn, self.ui.resetBtn):
            btn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
            btn.setMinimumHeight(30)

    # ─────────────────────────────────────────────────────────────────────
    # Posición absoluta 
    # ─────────────────────────────────────────────────────────────────────
    def handle_move_to_position(self):
        """Mueve el sistema a la posición absoluta indicada en los spinboxes"""
        x = self.ui.xPosition.value()
        y = self.ui.yPosition.value()
        z = self.ui.zPosition.value()
        velocity = self.ui.velocity_2.value()
        acceleration = self.ui.acceleration_2.value()

        print(f"Moving to absolute position → X: {x} mm | Y: {y} mm | Z: {z} mm")
        print(f"  Velocity: {velocity} mm/s | Acceleration: {acceleration} mm/s²")

        # Mover los tres ejes a la posición absoluta indicada
        self.controller.move_absolute([AXIS_X, AXIS_Y, AXIS_Z], [x, y, z], velocity, acceleration)

    def handle_reset_position(self):
        """Pone todos los spinboxes a 0 y manda el sistema a home"""
        for spinbox in (self.ui.xPosition, self.ui.yPosition, self.ui.zPosition):
            spinbox.setValue(0.0)

        print("Reset: all positions set to 0, returning shutter to home.")
        self.controller.home_axes([AXIS_X, AXIS_Y, AXIS_Z])

    # Escala (Auto) – espejo de setup_scale_selector en Manual 
    def _setup_scale_selector_auto(self):
        """Configura scaleList_2 igual que scaleList en Manual"""
        self.ui.scaleList_2.clear()
        scales = [
            ("nm", "Nanómetros (nm)"),
            ("μm", "Micrómetros (μm)"),
            ("mm", "Milímetros (mm)"),
            ("cm", "Centímetros (cm)"),
        ]
        for value, text in scales:
            self.ui.scaleList_2.addItem(text, value)
        # Misma selección por defecto que en Manual (mm = índice 2)
        self.ui.scaleList_2.setCurrentIndex(2)
        self.ui.scaleList_2.setFont(QFont("Sitka Small", 10))

    # Velocidad (Auto) 
    def _setup_velocity_selector_auto(self):
        """Configura velocity_2 igual que velocity en Manual"""
        self.ui.velocity_2.setFont(QFont("Sitka Small", 10))
        self.ui.velocity_2.setMinimum(0.1)
        self.ui.velocity_2.setMaximum(1000.0)
        self.ui.velocity_2.setSingleStep(0.1)
        self.ui.velocity_2.setDecimals(2)
        self.ui.velocity_2.setSuffix(" mm/s")
        self.ui.velocity_2.setValue(10.0)

    # Aceleración (Auto) 
    def _setup_acceleration_selector_auto(self):
        """Configura acceleration_2 igual que acceleration en Manual"""
        self.ui.acceleration_2.setFont(QFont("Sitka Small", 10))
        self.ui.acceleration_2.setMinimum(0.1)
        self.ui.acceleration_2.setMaximum(10000.0)
        self.ui.acceleration_2.setSingleStep(1.0)
        self.ui.acceleration_2.setDecimals(2)
        self.ui.acceleration_2.setSuffix(" mm/s²")
        self.ui.acceleration_2.setValue(100.0)

    # ============================================================
    # SECCIÓN SHUTTER – TIEMPO Y ESCALA DE TIEMPO
    # ============================================================
    # ─────────────────────────────────────────────────────────────────────
    # Modificación de la interfaz de usuario
    # ───────────────────────────────────────────────────────────────────── 
    def setup_shutter_section(self):
        """Configura la sección del shutter automático"""
        # Título
        self.ui.label_27.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.label_27.setStyleSheet("color: THEME.COLOR_TEXT_1;")

        # Imagen del gráfico de tiempo
        self.ui.timeGraph.setMaximumSize(QSize(300, 150))
        self.ui.timeGraph.setScaledContents(True)

        # Label "Delay time"
        self.ui.label_28.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.label_28.setStyleSheet("color: THEME.COLOR_TEXT_1;")

        # Label descriptivo (t1 / descripción)
        self.ui.label_29.setFont(QFont("Sitka Small", 8, italic=True))
        self.ui.label_29.setStyleSheet("color: THEME.COLOR_ACCENT_1;")

        # Label "Scale" del tiempo
        self.ui.label_42.setFont(QFont("Sitka Small", 10))
        self.ui.label_42.setStyleSheet("color: THEME.COLOR_TEXT_1;")

        # Selector de escala de tiempo
        self._setup_time_scale_selector()

        # SpinBox timeShutter (su sufijo se actualiza al cambiar la escala)
        self._setup_time_spinbox()

        # Botón Accept
        self._setup_accept_button()

    # Escala de tiempo 
    def _setup_time_scale_selector(self):
        """Configura scaleListTime con unidades de tiempo de ns a s"""
        self.ui.scaleListTime.clear()

        time_scales = [
            ("ns",  "Nanosegundos (ns)"),
            ("μs",  "Microsegundos (μs)"),
            ("ms",  "Milisegundos (ms)"),
            ("s",   "Segundos (s)"),
        ]
        for value, text in time_scales:
            self.ui.scaleListTime.addItem(text, value)

        # Segundos como unidad por defecto (índice 3)
        self.ui.scaleListTime.setCurrentIndex(3)
        self.ui.scaleListTime.setFont(QFont("Sitka Small", 10))

    def _on_time_scale_changed(self, index):
        """Actualiza el sufijo y el rango de timeShutter según la escala elegida"""
        unit = self.ui.scaleListTime.currentData()

        # Conversión desde segundos guardados → unidad mostrada
        factors = {"ns": 1e9, "μs": 1e6, "ms": 1e3, "s": 1.0}
        suffixes = {"ns": " ns", "μs": " μs", "ms": " ms", "s": " s"}
        max_values = {"ns": 1e10, "μs": 1e7, "ms": 1e4, "s": 10000.0}
        steps = {"ns": 1.0, "μs": 0.1, "ms": 0.001, "s": 0.001}
        decimals = {"ns": 0, "μs": 1, "ms": 3, "s": 3}

        factor = factors.get(unit, 1.0)

        self.ui.timeShutter.blockSignals(True)
        self.ui.timeShutter.setSuffix(suffixes.get(unit, " s"))
        self.ui.timeShutter.setMaximum(max_values.get(unit, 10000.0))
        self.ui.timeShutter.setSingleStep(steps.get(unit, 0.001))
        self.ui.timeShutter.setDecimals(decimals.get(unit, 3))
        # Mostrar el valor guardado convertido a la nueva unidad
        self.ui.timeShutter.setValue(self._saved_shutter_time_s * factor)
        self.ui.timeShutter.blockSignals(False)

    # SpinBox de tiempo 
    def _setup_time_spinbox(self):
        """Configura el QDoubleSpinBox timeShutter"""
        self.ui.timeShutter.setFont(QFont("Sitka Small", 10))
        self.ui.timeShutter.setMinimum(0.0)
        self.ui.timeShutter.setMaximum(10000.0)
        self.ui.timeShutter.setSingleStep(0.001)
        self.ui.timeShutter.setDecimals(3)
        self.ui.timeShutter.setSuffix(" s")
        self.ui.timeShutter.setValue(self._saved_shutter_time_s)
        self.ui.timeShutter.setMinimumWidth(130)

    # Botón Accept 
    def _setup_accept_button(self):
        """Configura el botón acceptBtn existente en la UI"""
        self.ui.acceptBtn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.acceptBtn.setMinimumHeight(30)

    # ─────────────────────────────────────────────────────────────────────
    # Tiempo del shutter
    # ───────────────────────────────────────────────────────────────────── 
    def handle_accept_shutter_time(self):
        """Guarda el valor de timeShutter (siempre en segundos internamente)"""
        unit = self.ui.scaleListTime.currentData()
        factors_to_s = {"ns": 1e-9, "μs": 1e-6, "ms": 1e-3, "s": 1.0}
        factor = factors_to_s.get(unit, 1.0)

        displayed_value = self.ui.timeShutter.value()
        self._saved_shutter_time_s = displayed_value * factor

        print(
            f"Shutter time saved: {displayed_value} {unit} "
            f"({self._saved_shutter_time_s:.9f} s)")

        # NOTA: sincronizar el shutter por hardware (PSO, disparo ligado a la
        # posición/tiempo real del drive) requiere configurar una ventana PSO
        # específica del cableado de la estación (eje, salida, modo de
        # distancia/tiempo) que no está definida en este proyecto. El valor
        # guardado aquí (self._saved_shutter_time_s) queda disponible para
        # una futura secuencia automática que abra/cierre el shutter por
        # software usando AerotechController.set_digital_output(...) junto
        # con un QTimer, en vez de temporización por hardware vía PSO.

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Tiempo Guardado")
        msg.setText("El tiempo de delay del shutter ha sido guardado:")
        msg.setInformativeText(
            f"{displayed_value} {unit}  ({self._saved_shutter_time_s:.6f} s)"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()