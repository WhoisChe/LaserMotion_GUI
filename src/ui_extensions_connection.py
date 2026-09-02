########################################################################
## CONNECTION PAGE EXTENSIONS
## Modificaciones de diseño para la página de conexión
########################################################################

import json
import os
import re

from PySide6.QtCore import Qt, QSize, QObject, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy, QMessageBox

import config
from src.color_contrast import readable_text_color

# Fichero local (no versionado, ver .gitignore) donde se guarda la última IP
# con la que se conectó con éxito, para precargarla en el futuro en vez del
# valor de fábrica.
LOCAL_SETTINGS_PATH = "local_connection_settings.json"
DEFAULT_HOST = "192.168.7.1"

_IPV4_RE = re.compile(
    r"^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$"
)
# Hostname básico (RFC 1123, simplificado): letras/dígitos/guiones, con
# puntos como separador de etiquetas, sin empezar/terminar en guión.
_HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)"
    r"(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)


def _is_valid_host(host: str) -> bool:
    """IPv4 básico o hostname — ver 06_connection.md §2."""
    host = host.strip()
    if not host:
        return False
    return bool(_IPV4_RE.match(host) or _HOSTNAME_RE.match(host))


class _ConnectWorker(QObject):
    """Ejecuta AerotechController.connect() fuera del hilo de la interfaz."""

    finished = Signal(bool)

    def __init__(self, controller, host):
        super().__init__()
        self._controller = controller
        self._host = host

    def run(self):
        ok = self._controller.connect(self._host)
        self.finished.emit(ok)


class ConnectionPageExtensions:
    """
    Extensiones de UI para la página de conexión.

    Reescrita en la migración de agosto de 2026 (06_connection.md):
    confirmado que el iSMC no se conecta por puerto serie/baudios, así que
    el selector de COM port y de baud rate se eliminaron por completo y se
    sustituyeron por un campo de IP (hostAddressInput). El mecanismo de
    conexión en QThread (_ConnectWorker) no se ha tocado — solo cambió de
    dónde sale el valor de host.
    """

    def __init__(self, ui, main_window, controller):
        self.ui = ui
        self.main = main_window
        # Instancia compartida de AerotechController (ver main.py)
        self.controller = controller
        self._connect_thread = None
        self._connect_worker = None

    def apply_modifications(self):
        """Aplica todas las modificaciones de la página de conexión"""
        self.setup_title()
        self.setup_host_address_input()
        self.setup_connect_button()

    def refresh_theme(self):
        """Reaplica el color de las etiquetas simples (título, label_21) que
        no están dentro de un botón/QLineEdit con su propio fondo — se
        fijaron una sola vez con el tema activo en ese momento, así que un
        cambio de tema en caliente las deja con el color del tema anterior
        (ver refresh_theme() en ManualPageExtensions, mismo motivo)."""
        self.ui.label_11.setStyleSheet(f"color: {config.THEME.COLOR_TEXT_1};")
        self.ui.label_21.setStyleSheet(f"color: {config.THEME.COLOR_TEXT_1};")

    def connect_signals(self):
        """Conecta las señales específicas de la página de conexión"""
        # El botón connectBtn ya está conectado en setup_connect_button()

    def setup_title(self):
        """Configura el título de la página"""
        self.ui.label_11.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.label_11.setStyleSheet(f"color: {config.THEME.COLOR_TEXT_1};")

    def setup_host_address_input(self):
        """Configura el campo de IP del controlador iSMC"""
        self.ui.label_21.setFont(QFont("Sitka Small", 10))
        self.ui.label_21.setStyleSheet(f"color: {config.THEME.COLOR_TEXT_1};")
        self.ui.label_21.setText("iSMC controller IP address")

        self.ui.hostAddressInput.setFont(QFont("Sitka Small", 10))
        self.ui.hostAddressInput.setStyleSheet(f"""
            QLineEdit {{
                background-color: {config.THEME.COLOR_BACKGROUND_2};
                color: {config.THEME.COLOR_TEXT_1};
                border: 2px solid {config.THEME.COLOR_ACCENT_3};
                border-radius: 5px;
                padding: 8px;
                min-height: 30px;
            }}
            QLineEdit:focus {{
                border: 2px solid {config.THEME.COLOR_ACCENT_1};
            }}
        """)

        # Precargar con self.controller.host si ya hubo un intento de
        # conexión en esta sesión; si no, con la última IP guardada
        # localmente; si tampoco existe, con el valor de fábrica.
        self.ui.hostAddressInput.setText(self.controller.host or self._load_last_host())

    def setup_connect_button(self):
        """Configura el botón de conectar"""
        self.ui.connectBtn.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.connectBtn.setMinimumHeight(50)
        self.ui.connectBtn.setCheckable(True)

        self.ui.connectBtn.setStyleSheet(f"""
            QPushButton {{
                background-color: {config.THEME.COLOR_BACKGROUND_2};
                color: {config.THEME.COLOR_TEXT_1};
                border: 2px solid {config.THEME.COLOR_ACCENT_3};
                border-radius: 10px;
                padding: 12px;
            }}
            QPushButton:hover {{
                background-color: {config.THEME.COLOR_ACCENT_2};
                color: {readable_text_color(config.THEME.COLOR_ACCENT_2)};
                border: 2px solid {config.THEME.COLOR_ACCENT_1};
            }}
            QPushButton:checked {{
                background-color: #2E7D32;
                color: white;
                border: 2px solid #1B5E20;
            }}
            QPushButton:checked:hover {{
                background-color: #1B5E20;
            }}
        """)

        # Conectar señal
        self.ui.connectBtn.clicked.connect(self.handle_connect_click)

    def handle_connect_click(self):
        """
        Maneja el clic del botón de conectar con el iSMC. Valida el formato
        de la IP antes de intentar nada, y lanza la conexión en un QThread
        para no congelar la interfaz mientras se establece (o falla) la
        comunicación con el controlador — mismo mecanismo de antes, solo
        cambia el origen del host.
        """
        if self.ui.connectBtn.isChecked():
            if self.controller.is_connected:
                self._on_connect_finished(True)
                return

            host = self.ui.hostAddressInput.text().strip()
            if not _is_valid_host(host):
                self.ui.connectBtn.setChecked(False)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Invalid address")
                msg.setText(f'"{host}" is not a valid IPv4 address or hostname.')
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
                return

            self.ui.connectBtn.setEnabled(False)
            self.ui.connectBtn.setText("Connecting...")

            self._connect_thread = QThread()
            self._connect_worker = _ConnectWorker(self.controller, host)
            self._connect_worker.moveToThread(self._connect_thread)
            self._connect_thread.started.connect(self._connect_worker.run)
            self._connect_worker.finished.connect(self._on_connect_finished)
            self._connect_worker.finished.connect(self._connect_thread.quit)
            self._connect_thread.finished.connect(self._connect_thread.deleteLater)
            self._connect_thread.start()

        else:
            print("[Aerotech] Desconectando...")
            self.controller.disconnect()
            self.ui.connectBtn.setText("Connect")

    def _on_connect_finished(self, connected):
        """Se ejecuta en el hilo de la UI cuando termina el intento de conexión."""
        self.ui.connectBtn.setEnabled(True)
        if connected:
            print("[Aerotech] Conexión establecida")
            self.ui.connectBtn.setText("Disconnect")
            # Tras una conexión exitosa con una IP distinta de la de
            # fábrica, se guarda localmente para precargarla en el futuro.
            if self.controller.host and self.controller.host != DEFAULT_HOST:
                self._save_last_host(self.controller.host)
        else:
            print("[Aerotech] No se pudo conectar con el iSMC")
            self.ui.connectBtn.setChecked(False)
            self.ui.connectBtn.setText("Connect")

    # ─────────────────────────────────────────────────────────────────────
    # Persistencia local de la última IP exitosa
    # ─────────────────────────────────────────────────────────────────────
    def _load_last_host(self):
        try:
            if os.path.exists(LOCAL_SETTINGS_PATH):
                with open(LOCAL_SETTINGS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                host = data.get("last_host")
                if host and _is_valid_host(host):
                    return host
        except Exception as e:
            print(f"[Connection] Error leyendo {LOCAL_SETTINGS_PATH}: {e}")
        return DEFAULT_HOST

    def _save_last_host(self, host):
        try:
            with open(LOCAL_SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump({"last_host": host}, f, indent=2)
        except Exception as e:
            print(f"[Connection] Error guardando {LOCAL_SETTINGS_PATH}: {e}")
