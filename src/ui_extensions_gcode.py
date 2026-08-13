########################################################################
## GCODE PAGE EXTENSIONS
########################################################################

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (QSizePolicy, QPushButton, QFileDialog,
                               QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox,
                               QLabel, QFrame)

from src.aerotech_controller import AXIS_X, AXIS_Y, AXIS_Z

# Comandos G-Code soportados por el intérprete: G0/G1 (movimiento lineal),
# G28 (home), G90/G91 (absoluto/relativo), M0 (pausa: deshabilita los ejes)
GCODE_SUPPORTED = {"G0", "G1", "G28", "G90", "G91", "M0"}

# Velocidad usada cuando la línea G-Code no especifica F (mm/s), y
# aceleración fija aplicada a los movimientos (mm/s²)
DEFAULT_FEED_MM_S = 50.0
DEFAULT_ACCEL_MM_S2 = 100.0


class GCodePageExtensions:
    """Extensiones de UI para la página G-Code"""

    def __init__(self, ui, main_window, controller):
        self.ui = ui
        self.main = main_window
        self.current_file_path = None
        self.gcode_content = ""
        self.gcode_saved = False            # Controla si el G-Code ha sido guardado
        self.remove_file_btn = None         # Botón para eliminar archivo cargado
        # Instancia compartida de AerotechController (ver src/ui_extensions.py)
        self.controller = controller
        self._absolute_mode = True          # Modo de coordenadas (True = absoluto, False = relativo)

    def apply_modifications(self):
        """Aplica todas las modificaciones de la página G-Code"""
        self.setup_title()
        self.setup_drag_drop_area()
        self.setup_buttons()
        
    def connect_signals(self):
        """Conecta las señales especí­ficas de la página G-Code"""
        # Conectar el botón Start
        self.ui.startBtn.clicked.connect(self.execute_gcode)
        # Conectar el botón Edit
        self.ui.editBtn.clicked.connect(self.reopen_gcode_editor)

    # ============================================================
    # EJECUCIÓN DE G-CODE via Automation1 API
    # ============================================================
    def execute_gcode(self):
        """"
        Parsea y ejecuta el G-Code cargado línea a línea usando el
        AerotechController compartido. Comandos soportados: G0, G1, G28,
        G90, G91, M0. La aceleración usada es DEFAULT_ACCEL_MM_S2 (no hay
        ningún parámetro G-Code estándar para aceleración).

        ATENCIÓN: cada línea se ejecuta de forma síncrona en el hilo de la
        interfaz (moveabsolute/moveincremental no bloquean, pero home() sí),
        así que un G28 en medio del programa congelará la UI hasta terminar
        el homing. Para producción, ejecutar en un QThread/worker.
        """
        if not self.current_file_path:
            print("Error: No G-Code file loaded")
            return

        self._absolute_mode = True
        lines = self.gcode_content.split("\n")
        print(f"[Aerotech] Ejecutando G-Code: {self.current_file_path} ({len(lines)} líneas)")

        for lineno, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line or line.startswith(";"):
                continue  # ignorar vacías y comentarios
            self._execute_gcode_line(lineno, line)

    # Intérprete de una línea G-Code
    def _execute_gcode_line(self, lineno, line):
        """
        Interpreta y ejecuta una línea G-Code.
        Extrae el comando (G0, G1, G28…) y los parámetros X, Y, Z, F.
        """
        tokens = line.upper().split()
        cmd = tokens[0] if tokens else ""

        # Extraer parámetros X, Y, Z, F de la línea
        params = {}
        for token in tokens[1:]:
            if token[0] in ("X", "Y", "Z", "F") and len(token) > 1:
                try:
                    params[token[0]] = float(token[1:])
                except ValueError:
                    pass

        if cmd not in GCODE_SUPPORTED:
            print(f"[L{lineno}] Comando '{cmd}' no soportado, omitido")
            return

        try:
            if cmd in ("G0", "G1"):
                # Movimiento lineal (rápido G0 o controlado G1)
                axes, deltas = [], []
                feed = params.get("F", DEFAULT_FEED_MM_S)

                for axis_name, axis in (("X", AXIS_X), ("Y", AXIS_Y), ("Z", AXIS_Z)):
                    if axis_name in params:
                        axes.append(axis)
                        deltas.append(params[axis_name])

                if axes:
                    if self._absolute_mode:
                        self.controller.move_absolute(axes, deltas, feed, DEFAULT_ACCEL_MM_S2)
                    else:
                        self.controller.move_incremental(axes, deltas, feed, DEFAULT_ACCEL_MM_S2)
                    print(f"[L{lineno}] {cmd} -> axes={axes} valores={deltas}")

            elif cmd == "G28":
                self.controller.home_axes([AXIS_X, AXIS_Y, AXIS_Z])
                print(f"[L{lineno}] G28 -> homing X, Y, Z")

            elif cmd == "G90":
                self._absolute_mode = True
                print(f"[L{lineno}] G90 -> modo absoluto")

            elif cmd == "G91":
                self._absolute_mode = False
                print(f"[L{lineno}] G91 -> modo relativo")

            elif cmd == "M0":
                # Pausa programada — deshabilita ejes momentáneamente
                self.controller.disable_axes([AXIS_X, AXIS_Y, AXIS_Z])
                print(f"[L{lineno}] M0 -> pausa (ejes deshabilitados)")

        except Exception as e:
            print(f"[Aerotech] Error ejecutando línea {lineno} '{line}': {e}")


    # ─────────────────────────────────────────────────────────────────────
    # Modificación de la interfaz de usuario
    # ─────────────────────────────────────────────────────────────────────     
    def setup_title(self):
        """Configura el tí­tulo de la página"""
        self.ui.label_9.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.label_9.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        
    def setup_drag_drop_area(self):
        """Configura el área de drag and drop"""
        # Habilitar drag and drop
        self.ui.dragYdrop.setAcceptDrops(True)
        
        # Configurar label dentro del área
        self.ui.label_6.setFont(QFont("Sitka Small", 10))
        self.ui.label_6.setStyleSheet("color: THEME.COLOR_TEXT_2;")
        self.ui.label_6.setText("Drag and drop your G-Code file here\nor click 'Select File' button")
        
        # Crear botón de eliminar archivo (inicialmente oculto)
        self.remove_file_btn = QPushButton("✕", self.ui.dragYdrop)
        self.remove_file_btn.setFont(QFont("Sitka Small", 8, QFont.Weight.Bold))
        self.remove_file_btn.setFixedSize(QSize(25, 25))
        self.remove_file_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: 2px solid #d32f2f;
                border-radius: 15px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
                border: 2px solid #b71c1c;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        self.remove_file_btn.setToolTip("Remove loaded file")
        self.remove_file_btn.clicked.connect(self.remove_loaded_file)
        self.remove_file_btn.hide()  # Oculto por defecto
        
        # Posicionar el botón en la esquina superior derecha del frame
        self.position_remove_button()
        
        # Instalar event filter personalizado
        self.ui.dragYdrop.dragEnterEvent = self.drag_enter_event
        self.ui.dragYdrop.dropEvent = self.drop_event
        
    def position_remove_button(self):
        """Posiciona el botón de eliminar en la esquina superior derecha"""
        if self.remove_file_btn:
            frame_width = self.ui.dragYdrop.width()
            frame_height = self.ui.dragYdrop.height()
            button_size = 25
            
            # Centrar verticalmente y posicionar a la derecha
            x_pos = frame_width - button_size - 10
            y_pos = (frame_height - button_size) // 2  # ← CENTRADO VERTICAL
            
            self.remove_file_btn.move(x_pos, y_pos)
        
    def drag_enter_event(self, event: QDragEnterEvent):
        """Maneja el evento de arrastrar archivo sobre el área"""
        if event.mimeData().hasUrls():
            # Verificar si es un archivo válido
            urls = event.mimeData().urls()
            if urls and len(urls) > 0:
                file_path = urls[0].toLocalFile()
                if file_path.lower().endswith(('.gcode', '.nc', '.txt')):
                    event.acceptProposedAction()
                    # Cambiar apariencia
                    self.ui.dragYdrop.setStyleSheet("""
                        QFrame {
                            background-color: THEME.COLOR_ACCENT_2;
                            border: 3px dashed THEME.COLOR_ACCENT_1;
                            border-radius: 15px;
                        }
                    """)
        
    def drop_event(self, event: QDropEvent):
        """Maneja el evento de soltar archivo en el área"""
        urls = event.mimeData().urls()
        if urls and len(urls) > 0:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.gcode', '.nc', '.txt')):
                self.load_gcode_file(file_path)
                event.acceptProposedAction()
        
        # Restaurar apariencia normal
        self.ui.dragYdrop.setStyleSheet("""
            QFrame {
                background-color: THEME.COLOR_BACKGROUND_3;
                border: 3px dashed THEME.COLOR_ACCENT_1;
                border-radius: 15px;
            }
        """)
        
    def setup_buttons(self):
        """Configura los botones de la página"""
        # Botón Select File
        self.ui.selectFileBtn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.selectFileBtn.setMinimumHeight(30)
        
        # Conectar señal
        self.ui.selectFileBtn.clicked.connect(self.select_file)
        
        # Botón Start
        self.ui.startBtn.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.startBtn.setMinimumHeight(35)
        self.ui.startBtn.setEnabled(False)  # Deshabilitado por defecto
        
        # Botón Edit
        self.ui.editBtn.setFont(QFont("Sitka Small", 10, QFont.Weight.Bold))
        self.ui.editBtn.setMinimumHeight(30)
        self.ui.editBtn.setEnabled(False)  # Deshabilitado por defecto hasta cargar archivo
        
    def select_file(self):
        """Abre diálogo para seleccionar archivo G-Code"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.main,
            "Select G-Code File",
            "",
            "G-Code Files (*.gcode *.nc *.txt);;All Files (*.*)"
        )
        
        if file_path:
            self.load_gcode_file(file_path)
            
    def load_gcode_file(self, file_path):
        """Carga un archivo G-Code"""
        try:
            with open(file_path, 'r') as file:
                self.gcode_content = file.read()
                self.current_file_path = file_path
                
            # Actualizar UI
            file_name = file_path.split('/')[-1]
            self.ui.label_6.setText(f"File loaded: {file_name}")
            self.ui.label_6.setStyleSheet("color: #769947; font-weight: bold;")
            
            # Resetear estado de guardado
            self.gcode_saved = False
            
            # NO habilitar botón Start hasta que se guarde
            self.ui.startBtn.setEnabled(False)
            
            # Habilitar botón Edit
            self.ui.editBtn.setEnabled(True)
            
            # Mostrar botón de eliminar archivo
            if self.remove_file_btn:
                self.position_remove_button()
                self.remove_file_btn.show()
            
            # Mostrar editor de G-Code
            self.show_gcode_editor()
            
        except Exception as e:
            self.ui.label_6.setText(f"Error loading file: {str(e)}")
            self.ui.label_6.setStyleSheet("color: #F44336; font-weight: bold;")

    def show_gcode_editor(self):
        """Muestra ventana de edición de G-Code"""
        # Guardar estado anterior por si se cancela
        was_saved_before = self.gcode_saved
        
        editor_dialog = GCodeEditorDialog(
            self.main,
            self.gcode_content,
            self.current_file_path
        )
        
        result = editor_dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            # Guardar cambios
            new_content = editor_dialog.get_content()
            if new_content != self.gcode_content:
                self.save_gcode_changes(new_content)
            else:
                # Aunque no haya cambios, marcar como guardado
                self.gcode_saved = True
                self.ui.startBtn.setEnabled(True)
        else:
            # Se presionó Cancel
            if not was_saved_before:
                # Si no había documento guardado antes, resetear todo
                self.cancel_file_load()
            # Si ya estaba guardado, no hacer nada (mantener estado anterior)
                
    def save_gcode_changes(self, new_content):
        """Guarda los cambios en el archivo G-Code"""
        try:
            with open(self.current_file_path, 'w') as file:
                file.write(new_content)
            self.gcode_content = new_content
            self.gcode_saved = True
            
            # Habilitar botón Start después de guardar
            self.ui.startBtn.setEnabled(True)
            
            print(f"G-Code file updated: {self.current_file_path}")
        except Exception as e:
            print(f"Error saving G-Code file: {str(e)}")
    
    def reopen_gcode_editor(self):
        """Reabre la ventana de edición de G-Code"""
        if not self.current_file_path or not self.gcode_content:
            print("No G-Code file loaded to edit")
            return
            
        # Mostrar editor de G-Code nuevamente
        self.show_gcode_editor()
    
    def cancel_file_load(self):
        """Cancela la carga del archivo y resetea el estado"""
        # Limpiar datos del archivo
        self.current_file_path = None
        self.gcode_content = ""
        self.gcode_saved = False
        
        # Resetear UI
        self.ui.label_6.setText("Drag and drop your G-Code file here\nor click 'Select File' button")
        self.ui.label_6.setStyleSheet("color: THEME.COLOR_TEXT_2;")
        
        # Deshabilitar botones
        self.ui.startBtn.setEnabled(False)
        self.ui.editBtn.setEnabled(False)
        
        # Ocultar botón de eliminar
        if self.remove_file_btn:
            self.remove_file_btn.hide()
        
        print("File load cancelled")
    
    def remove_loaded_file(self):
        """Elimina el archivo cargado y resetea al estado inicial"""
        # Usar el mismo método que cancel_file_load
        self.cancel_file_load()
        print("Loaded file removed")


# ─────────────────────────────────────────────────────────────────────
# Ventana de edición de G-Code
# ───────────────────────────────────────────────────────────────────── 
class GCodeEditorDialog(QDialog):
    """Diálogo para editar código G-Code"""
    
    def __init__(self, parent, content, file_path):
        super().__init__(parent)
        self.setWindowTitle(f"Edit G-Code: {file_path.split('/')[-1]}")
        self.setMinimumSize(QSize(800, 600))
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Tí­tulo
        title_label = QLabel("G-Code Editor")
        title_label.setFont(QFont("Sitka Small", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel#titleLabel {
                background-color: #F5F5F5;
                color: THEME.COLOR_TEXT_1;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        # Información del archivo
        info_label = QLabel(f"File: {file_path}")
        info_label.setFont(QFont("Sitka Small", 9))
        info_label.setStyleSheet("""
            QLabel#infoLabel {
                background-color: #F5F5F5;
                color: THEME.COLOR_ACCENT_2;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        layout.addWidget(info_label)
        
        # Editor de texto
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Courier New", 10))
        self.text_edit.setPlainText(content)
        self.text_edit.setStyleSheet("""
            QTextEdit{
                background-color: #2B2B2B;
                color: #F0F0F0;
                border: 2px solid #555;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.text_edit)
        
        # Información de ayuda
        help_label = QLabel("Tip: Edit your G-Code and click 'Save' to update the file")
        help_label.setFont(QFont("Sitka Small", 9))
        help_label.setStyleSheet("""
            QLabel#helpLabel {
                background-color: #F5F5F5;
                color: THEME.COLOR_ACCENT_2;
                padding: 8px;
                border-radius: 3px;
                font-style: italic;
            }
        """)
        layout.addWidget(help_label)
        
        # Botones
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.setFont(QFont("Sitka Small", 10))
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Estilo del diálogo
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
            }
            QPushButton {
                min-width: 100px;
                min-height: 35px;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
    def get_content(self):
        """Retorna el contenido editado"""
        return self.text_edit.toPlainText()