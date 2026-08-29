########################################################################
## AUTO PAGE EXTENSIONS
########################################################################
## Reescrita por completo en la migración de agosto de 2026
## (03_auto.md): Auto deja de ejecutar movimiento directamente y pasa a ser
## un generador de G-Code con 5 modos (Single point, Fixed-distance firing,
## Point array, Power gradient, Binary pattern).
########################################################################

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMessageBox, QFileDialog

import config
from src.aerotech_controller import AXIS_X, AXIS_Y, AXIS_Z

AXIS_CONST = {"X": AXIS_X, "Y": AXIS_Y, "Z": AXIS_Z}

DISTANCE_FACTORS_TO_MM = {"nm": 1e-6, "μm": 1e-3, "mm": 1.0, "cm": 10.0}
TIME_FACTORS_TO_S = {"ns": 1e-9, "μs": 1e-6, "ms": 1e-3, "s": 1.0}


class AutoPageExtensions:
    """Extensiones de UI para la página Auto Mode — generador de G-Code."""

    def __init__(self, ui, main_window, controller):
        self.ui = ui
        self.main = main_window
        self.controller = controller
        # Pasadas de "Point array": lista de {"axis": "X"|"Y", "start": float,
        # "end": float, "cross": float}
        self._pass_list = []

    def apply_modifications(self):
        """Aplica todas las modificaciones de la página Auto"""
        self.setup_axis_control_section()
        self.setup_mode_selector()
        self.setup_panels()
        self.setup_preview_and_buttons()
        self.update_preview()

    def connect_signals(self):
        """Conecta las señales específicas de la página Auto"""
        # Control por eje: enable/disable + home (copia propia de Auto)
        self.ui.toggleAutoXBtn.clicked.connect(lambda: self.handle_toggle_axis("X"))
        self.ui.toggleAutoYBtn.clicked.connect(lambda: self.handle_toggle_axis("Y"))
        self.ui.toggleAutoZBtn.clicked.connect(lambda: self.handle_toggle_axis("Z"))
        self.ui.homeAutoXBtn.clicked.connect(lambda: self.controller.home_axes([AXIS_X]))
        self.ui.homeAutoYBtn.clicked.connect(lambda: self.controller.home_axes([AXIS_Y]))
        self.ui.homeAutoZBtn.clicked.connect(lambda: self.controller.home_axes([AXIS_Z]))

        # Selector de modo -> cambia el panel visible y regenera el preview
        self.ui.modeSelector.currentIndexChanged.connect(self.ui.modeStack.setCurrentIndex)
        self.ui.modeSelector.currentIndexChanged.connect(self.update_preview)

        # Power gradient: Linear/Radial cambia el sub-panel visible
        self.ui.pgTypeCombo.currentIndexChanged.connect(self.ui.pgTypeStack.setCurrentIndex)
        self.ui.pgTypeCombo.currentIndexChanged.connect(self.update_preview)

        # Point array: añadir/quitar pasadas
        self.ui.paAddPassBtn.clicked.connect(self.add_pass)
        self.ui.paRemovePassBtn.clicked.connect(self.remove_selected_pass)

        # Cualquier cambio en cualquier campo regenera el preview en vivo
        for spinbox in self._all_spinboxes():
            spinbox.valueChanged.connect(self.update_preview)
        for combo in self._all_combos():
            combo.currentIndexChanged.connect(self.update_preview)
        for checkbox in (self.ui.spFireCheck, self.ui.fdLimitWindow, self.ui.paLimitWindow):
            checkbox.stateChanged.connect(self.update_preview)
        for toggle in self._bit_toggles():
            toggle.clicked.connect(self.update_preview)

        # Botones de salida
        self.ui.openInGCodeBtn.clicked.connect(self.handle_open_in_gcode)
        self.ui.downloadFileBtn.clicked.connect(self.handle_download_file)

    # ─────────────────────────────────────────────────────────────────────
    # Control por eje: Enable/Disable + Home
    # ─────────────────────────────────────────────────────────────────────
    def handle_toggle_axis(self, axis):
        """El botón mantiene siempre el texto "Enable" — el estado
        enabled/disabled ya lo indica el color vía QPushButton:checked
        (mismo patrón que Manual, ver ManualPageExtensions.handle_toggle_axis)."""
        btn = {"X": self.ui.toggleAutoXBtn, "Y": self.ui.toggleAutoYBtn, "Z": self.ui.toggleAutoZBtn}[axis]
        axis_const = AXIS_CONST[axis]
        if btn.isChecked():
            self.controller.enable_axes([axis_const])
        else:
            self.controller.disable_axes([axis_const])

    # ─────────────────────────────────────────────────────────────────────
    # Point array: gestión de pasadas
    # ─────────────────────────────────────────────────────────────────────
    def add_pass(self):
        axis = self.ui.paAxisCombo.currentText()
        start = self.ui.paStart.value()
        end = self.ui.paEnd.value()
        cross = self.ui.paCross.value()
        self._pass_list.append({"axis": axis, "start": start, "end": end, "cross": cross})
        cross_axis = "Y" if axis == "X" else "X"
        self.ui.paPassesList.addItem(f"{axis}: {start:.3f} → {end:.3f} mm  @ {cross_axis}={cross:.3f}")
        self.update_preview()

    def remove_selected_pass(self):
        row = self.ui.paPassesList.currentRow()
        if row >= 0:
            self.ui.paPassesList.takeItem(row)
            del self._pass_list[row]
            self.update_preview()

    # ─────────────────────────────────────────────────────────────────────
    # Generación de G-Code (directriz 2.2 de 03_auto.md)
    # ─────────────────────────────────────────────────────────────────────
    def update_preview(self):
        """Regenera el G-Code del modo activo y lo muestra en el preview."""
        generators = [
            self._generate_single_point,
            self._generate_fixed_distance,
            self._generate_point_array,
            self._generate_power_gradient,
            self._generate_binary_pattern,
        ]
        mode_index = self.ui.modeSelector.currentIndex()
        if not (0 <= mode_index < len(generators)):
            return
        lines = generators[mode_index]()
        if lines is None:
            # Validación contra la ventana de Calibration falló — no se
            # sobreescribe el preview con un resultado inválido.
            return
        self.ui.gcodePreviewAuto.setPlainText("\n".join(["G28"] + lines + ["G28"]))

    def _generate_single_point(self):
        x, y, z = self.ui.spX.value(), self.ui.spY.value(), self.ui.spZ.value()
        lines = [f"G0 X{x:.4f} Y{y:.4f} Z{z:.4f}"]
        if self.ui.spFireCheck.isChecked():
            duration_s = self.ui.spDuration.value() * TIME_FACTORS_TO_S.get(self.ui.spDurationScale.currentData(), 1.0)
            duration_us = duration_s * 1e6
            # Single point no tiene campo de potencia propio en la tabla de
            # 03_auto.md §1.2 — se dispara a 100% durante la duración indicada.
            lines.append("M3 S100")
            lines.append(f"G4 P{duration_us:.0f}")
            lines.append("M5")
        return lines

    def _generate_fixed_distance(self):
        sx, sy = self.ui.fdStartX.value(), self.ui.fdStartY.value()
        ex, ey = self.ui.fdEndX.value(), self.ui.fdEndY.value()

        if self.ui.fdLimitWindow.isChecked() and not self._validate_window([(sx, sy), (ex, ey)]):
            return None

        distance_mm = self.ui.fdDistance.value() * DISTANCE_FACTORS_TO_MM.get(self.ui.fdDistanceScale.currentData(), 1.0)
        pulses = self.ui.fdPulses.value()
        power = self.ui.fdPower.value()
        speed = self.ui.fdTravelSpeed.value()

        return [
            f"G0 X{sx:.4f} Y{sy:.4f}",
            f"M900 D{distance_mm:.4f} P{pulses}",
            f"M3 S{power:.0f}",
            f"G1 X{ex:.4f} Y{ey:.4f} F{speed:.2f}",
            "M5",
        ]

    def _generate_point_array(self):
        if not self._pass_list:
            return []

        distance_mm = self.ui.paDistance.value() * DISTANCE_FACTORS_TO_MM.get(self.ui.paDistanceScale.currentData(), 1.0)
        pulses = self.ui.paPulses.value()
        power = self.ui.paPower.value()
        speed = self.ui.paTravelSpeed.value()
        uniform = self.ui.paSpacingCombo.currentText() == "Uniform"

        lines = []
        for p in self._pass_list:
            if p["axis"] == "X":
                start_point, end_point = (p["start"], p["cross"]), (p["end"], p["cross"])
            else:
                start_point, end_point = (p["cross"], p["start"]), (p["cross"], p["end"])

            if self.ui.paLimitWindow.isChecked() and not self._validate_window([start_point, end_point]):
                return None

            lines.append(f"G0 X{start_point[0]:.4f} Y{start_point[1]:.4f}")
            if not uniform:
                # TODO: el espaciado "Irregular" requiere
                # pso_configure_array_distances() con una lista de distancias
                # punto a punto; esta UI aún no captura esa lista, así que se
                # usa M900 con la distancia fija como aproximación hasta
                # definir cómo introducir espaciados irregulares en pantalla.
                pass
            lines.append(f"M900 D{distance_mm:.4f} P{pulses}")
            lines.append(f"M3 S{power:.0f}")
            lines.append(f"G1 X{end_point[0]:.4f} Y{end_point[1]:.4f} F{speed:.2f}")
            lines.append("M5")
        return lines

    def _generate_power_gradient(self):
        gradient_type = self.ui.pgTypeCombo.currentText()
        distance_mm = self.ui.pgDistance.value() * DISTANCE_FACTORS_TO_MM.get(self.ui.pgDistanceScale.currentData(), 1.0)
        power_start = self.ui.pgPowerStart.value()
        power_end = self.ui.pgPowerEnd.value()
        speed = self.ui.pgTravelSpeed.value()

        if gradient_type == "Radial":
            cx, cy, radius = self.ui.pgCenterX.value(), self.ui.pgCenterY.value(), self.ui.pgRadius.value()
            sx, sy = cx + radius, cy
            ex, ey = cx - radius, cy
            total_dist = 2 * radius
        else:
            sx, sy = self.ui.pgStartX.value(), self.ui.pgStartY.value()
            ex, ey = self.ui.pgEndX.value(), self.ui.pgEndY.value()
            total_dist = ((ex - sx) ** 2 + (ey - sy) ** 2) ** 0.5

        n_segments = max(1, round(total_dist / distance_mm)) if distance_mm > 0 and total_dist > 0 else 1

        # Siempre segmentado (G1 cortos + M3 S<valor> escalonado), nunca
        # array PSO nativo — ver label_pgSegmentedWarning en el panel.
        lines = [f"G0 X{sx:.4f} Y{sy:.4f}"]
        for i in range(n_segments):
            t_mid = (i + 0.5) / n_segments
            t_end = (i + 1) / n_segments
            x1 = sx + (ex - sx) * t_end
            y1 = sy + (ey - sy) * t_end
            power = power_start + (power_end - power_start) * t_mid
            lines.append(f"M3 S{power:.1f}")
            lines.append(f"G1 X{x1:.4f} Y{y1:.4f} F{speed:.2f}")
        lines.append("M5")
        return lines

    def _generate_binary_pattern(self):
        sx, sy = self.ui.bpStartX.value(), self.ui.bpStartY.value()
        ex, ey = self.ui.bpEndX.value(), self.ui.bpEndY.value()
        distance_mm = self.ui.bpDistance.value() * DISTANCE_FACTORS_TO_MM.get(self.ui.bpDistanceScale.currentData(), 1.0)
        speed = self.ui.bpTravelSpeed.value()
        bits = "".join("1" if toggle.isChecked() else "0" for toggle in self._bit_toggles())

        # El dialecto G-Code de 04_gcode.md no define un M-code para un
        # patrón de bits — se deja como comentario informativo (el
        # intérprete ignora líneas que empiezan por ";"); la ejecución real
        # del patrón pasaría por controller.pso_configure_bitmap() de forma
        # directa, no a través de este texto.
        return [
            f"G0 X{sx:.4f} Y{sy:.4f}",
            f"M900 D{distance_mm:.4f} P1",
            f"; binary pattern {bits} — see pso_configure_bitmap()",
            f"G1 X{ex:.4f} Y{ey:.4f} F{speed:.2f}",
        ]

    def _validate_window(self, points):
        """Valida una lista de puntos (x, y) contra la ventana maestra de
        Calibration. Si todavía no hay ventana calibrada, deja pasar (no hay
        nada contra qué validar)."""
        try:
            window = self.main.ui_ext.calibration_ext.get_safety_window()
        except Exception:
            window = None
        if not window:
            return True
        for x, y in points:
            if not (window["x_min"] <= x <= window["x_max"] and window["y_min"] <= y <= window["y_max"]):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Outside safety window")
                msg.setText(f"Point ({x:.3f}, {y:.3f}) mm is outside the calibrated position window.")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
                return False
        return True

    # ─────────────────────────────────────────────────────────────────────
    # Botones de salida
    # ─────────────────────────────────────────────────────────────────────
    def handle_open_in_gcode(self):
        text = self.ui.gcodePreviewAuto.toPlainText()
        if not text.strip():
            return
        self.main.ui_ext.gcode_ext.load_gcode_text(text)

    def handle_download_file(self):
        text = self.ui.gcodePreviewAuto.toPlainText()
        if not text.strip():
            return
        file_path, _ = QFileDialog.getSaveFileName(self.main, "Download G-Code", "", "G-Code Files (*.gcode)")
        if file_path:
            with open(file_path, "w") as f:
                f.write(text)

    # ─────────────────────────────────────────────────────────────────────
    # Modificación de la interfaz de usuario
    # ─────────────────────────────────────────────────────────────────────
    def _all_spinboxes(self):
        return [
            self.ui.spX, self.ui.spY, self.ui.spZ, self.ui.spDuration,
            self.ui.fdStartX, self.ui.fdStartY, self.ui.fdEndX, self.ui.fdEndY,
            self.ui.fdDistance, self.ui.fdPulses, self.ui.fdPower, self.ui.fdTravelSpeed,
            self.ui.paStart, self.ui.paEnd, self.ui.paCross,
            self.ui.paDistance, self.ui.paPulses, self.ui.paPower, self.ui.paTravelSpeed,
            self.ui.pgStartX, self.ui.pgStartY, self.ui.pgEndX, self.ui.pgEndY,
            self.ui.pgCenterX, self.ui.pgCenterY, self.ui.pgRadius,
            self.ui.pgDistance, self.ui.pgPowerStart, self.ui.pgPowerEnd, self.ui.pgTravelSpeed,
            self.ui.bpStartX, self.ui.bpStartY, self.ui.bpEndX, self.ui.bpEndY,
            self.ui.bpDistance, self.ui.bpTravelSpeed,
        ]

    def _all_combos(self):
        return [
            self.ui.spDurationScale, self.ui.fdDistanceScale,
            self.ui.paAxisCombo, self.ui.paSpacingCombo, self.ui.paDistanceScale,
            self.ui.pgTypeCombo, self.ui.pgDistanceScale, self.ui.bpDistanceScale,
        ]

    def _bit_toggles(self):
        return [
            self.ui.bpBitToggle0, self.ui.bpBitToggle1, self.ui.bpBitToggle2, self.ui.bpBitToggle3,
            self.ui.bpBitToggle4, self.ui.bpBitToggle5, self.ui.bpBitToggle6, self.ui.bpBitToggle7,
        ]

    def setup_axis_control_section(self):
        """Configura los 3 bloques de control por eje (Enable/Disable, Home)"""
        axis_specs = [
            (self.ui.labelAxisAutoX, self.ui.toggleAutoXBtn, self.ui.homeAutoXBtn),
            (self.ui.labelAxisAutoY, self.ui.toggleAutoYBtn, self.ui.homeAutoYBtn),
            (self.ui.labelAxisAutoZ, self.ui.toggleAutoZBtn, self.ui.homeAutoZBtn),
        ]
        toggle_style = f"""
            QPushButton {{
                background-color: {config.THEME.COLOR_BACKGROUND_2};
                color: {config.THEME.COLOR_TEXT_1};
                border: 2px solid {config.THEME.COLOR_ACCENT_3};
                border-radius: 8px;
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: {config.THEME.COLOR_ACCENT_2};
                color: white;
                border: 2px solid {config.THEME.COLOR_ACCENT_1};
            }}
            QPushButton:checked {{
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
            }}
        """
        home_style = f"""
            QPushButton {{
                background-color: {config.THEME.COLOR_BACKGROUND_2};
                color: {config.THEME.COLOR_TEXT_1};
                border: 2px solid {config.THEME.COLOR_ACCENT_3};
                border-radius: 8px;
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: {config.THEME.COLOR_ACCENT_1};
                color: white;
            }}
        """
        for label, toggle_btn, home_btn in axis_specs:
            label.setFont(QFont("Sitka Small", 13, QFont.Weight.Bold))
            label.setStyleSheet(f"color: {config.THEME.COLOR_TEXT_1};")
            toggle_btn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
            toggle_btn.setMinimumHeight(40)
            toggle_btn.setStyleSheet(toggle_style)
            toggle_btn.setText("Enable")
            home_btn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
            home_btn.setMinimumHeight(36)
            home_btn.setStyleSheet(home_style)

    def setup_mode_selector(self):
        self.ui.label_autoMode.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.label_autoMode.setStyleSheet(f"color: {config.THEME.COLOR_TEXT_1};")
        self.ui.modeSelector.clear()
        self.ui.modeSelector.addItems([
            "Single point",
            "Fixed-distance firing",
            "Point array",
            "Power gradient",
            "Binary pattern",
        ])
        self.ui.modeSelector.setFont(QFont("Sitka Small", 10))

    def setup_panels(self):
        for spinbox in self._all_spinboxes():
            if spinbox not in (self.ui.fdPulses, self.ui.paPulses):
                spinbox.setDecimals(3)
        # Rangos de posición (mm)
        for spinbox in (self.ui.spX, self.ui.spY, self.ui.spZ,
                        self.ui.fdStartX, self.ui.fdStartY, self.ui.fdEndX, self.ui.fdEndY,
                        self.ui.paStart, self.ui.paEnd, self.ui.paCross,
                        self.ui.pgStartX, self.ui.pgStartY, self.ui.pgEndX, self.ui.pgEndY,
                        self.ui.pgCenterX, self.ui.pgCenterY, self.ui.pgRadius,
                        self.ui.bpStartX, self.ui.bpStartY, self.ui.bpEndX, self.ui.bpEndY):
            spinbox.setMinimum(-1000.0)
            spinbox.setMaximum(1000.0)
            spinbox.setSuffix(" mm")
        # Distancia entre eventos (valor sin unidad, unidad va en el combo)
        for spinbox in (self.ui.fdDistance, self.ui.paDistance, self.ui.pgDistance, self.ui.bpDistance):
            spinbox.setMinimum(0.0)
            spinbox.setMaximum(100000.0)
        # Potencia (%)
        for spinbox in (self.ui.fdPower, self.ui.paPower, self.ui.pgPowerStart, self.ui.pgPowerEnd):
            spinbox.setMinimum(0.0)
            spinbox.setMaximum(100.0)
            spinbox.setSuffix(" %")
        self.ui.pgPowerEnd.setValue(100.0)
        # Velocidad de desplazamiento (mm/s)
        for spinbox in (self.ui.fdTravelSpeed, self.ui.paTravelSpeed, self.ui.pgTravelSpeed, self.ui.bpTravelSpeed):
            spinbox.setMinimum(0.1)
            spinbox.setMaximum(1000.0)
            spinbox.setValue(10.0)
            spinbox.setSuffix(" mm/s")
        # Pulsos por evento
        for spinbox in (self.ui.fdPulses, self.ui.paPulses):
            spinbox.setMinimum(1)
            spinbox.setMaximum(1000)
            spinbox.setValue(1)
        # Duración (Single point)
        self.ui.spDuration.setMinimum(0.0)
        self.ui.spDuration.setMaximum(1000000.0)
        self.ui.spDuration.setValue(1.0)

        # Combos de escala de distancia (nm/μm/mm/cm)
        for combo in (self.ui.fdDistanceScale, self.ui.paDistanceScale, self.ui.pgDistanceScale, self.ui.bpDistanceScale):
            combo.clear()
            for value, text in (("nm", "Nanometers (nm)"), ("μm", "Micrometers (μm)"),
                                 ("mm", "Millimeters (mm)"), ("cm", "Centimeters (cm)")):
                combo.addItem(text, value)
            combo.setCurrentIndex(2)
            combo.setFont(QFont("Sitka Small", 9))

        # Combo de escala de tiempo (ns/μs/ms/s)
        self.ui.spDurationScale.clear()
        for value, text in (("ns", "Nanoseconds (ns)"), ("μs", "Microseconds (μs)"),
                             ("ms", "Milliseconds (ms)"), ("s", "Seconds (s)")):
            self.ui.spDurationScale.addItem(text, value)
        self.ui.spDurationScale.setCurrentIndex(3)
        self.ui.spDurationScale.setFont(QFont("Sitka Small", 9))

        # Point array: eje + espaciado
        self.ui.paAxisCombo.clear()
        self.ui.paAxisCombo.addItems(["X", "Y"])
        self.ui.paSpacingCombo.clear()
        self.ui.paSpacingCombo.addItems(["Uniform", "Irregular"])

        # Power gradient: tipo + sub-panel
        self.ui.pgTypeCombo.clear()
        self.ui.pgTypeCombo.addItems(["Linear", "Radial"])
        self.ui.pgTypeStack.setCurrentIndex(0)
        self.ui.label_pgSegmentedWarning.setStyleSheet("color: #FFA726; font-style: italic;")

        # Estilo general de labels de los 5 paneles
        for label in (self.ui.label_spPosition, self.ui.label_spDuration,
                      self.ui.label_fdStart, self.ui.label_fdEnd, self.ui.label_fdDistance,
                      self.ui.label_fdPulses, self.ui.label_fdPower, self.ui.label_fdTravelSpeed,
                      self.ui.label_paSpacing, self.ui.label_paDistance, self.ui.label_paPulses,
                      self.ui.label_paPower, self.ui.label_paTravelSpeed,
                      self.ui.label_pgType, self.ui.label_pgLinearStart, self.ui.label_pgLinearEnd,
                      self.ui.label_pgCenter, self.ui.label_pgRadius, self.ui.label_pgDistance,
                      self.ui.label_pgPower, self.ui.label_pgTravelSpeed,
                      self.ui.label_bpStart, self.ui.label_bpEnd, self.ui.label_bpDistance,
                      self.ui.label_bpPattern, self.ui.label_bpTravelSpeed):
            label.setFont(QFont("Sitka Small", 9, QFont.Weight.Bold))
            label.setStyleSheet(f"color: {config.THEME.COLOR_TEXT_1};")

        for toggle in self._bit_toggles():
            toggle.setFont(QFont("Sitka Small", 9))

    def setup_preview_and_buttons(self):
        self.ui.label_autoPreview.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.label_autoPreview.setStyleSheet(f"color: {config.THEME.COLOR_TEXT_1};")
        self.ui.gcodePreviewAuto.setStyleSheet("""
            QTextEdit {
                background-color: #2B2B2B;
                color: #F0F0F0;
                border: 2px solid #555;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        for btn in (self.ui.openInGCodeBtn, self.ui.downloadFileBtn):
            btn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
            btn.setMinimumHeight(32)
