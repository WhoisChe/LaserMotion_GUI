########################################################################
## CONNECTION PAGE EXTENSIONS
## Modificaciones de diseño para la página de conexión
########################################################################

from PySide6.QtCore import Qt, QSize, QObject, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtSerialPort import QSerialPortInfo


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

    NOTA: el controlador Aerotech Automation1-iSMC NO se conecta por puerto
    serie/baud rate, sino por red/local con Controller.connect(host). Además,
    esa llamada es bloqueante y puede tardar mucho si no hay hardware
    escuchando, así que el botón "Connect" de esta página la lanza en un
    QThread aparte en vez de conectar automáticamente al arrancar la app.
    El selector de puerto COM y baud rate queda disponible para un posible
    dispositivo serie auxiliar (p. ej. un Arduino), no para el iSMC.
    """

    def __init__(self, ui, main_window, controller):
        self.ui = ui
        self.main = main_window
        # Instancia compartida de AerotechController (ver src/ui_extensions.py)
        self.controller = controller
        self._connect_thread = None
        self._connect_worker = None

    def apply_modifications(self):
        """Aplica todas las modificaciones de la página de conexión"""
        self.setup_title()
        self.setup_com_port_selector()
        self.setup_baud_rate_selector()
        self.setup_connect_button()
        
    def connect_signals(self):
        """Conecta las señales específicas de la página de conexión"""
        # El botón connectBtn ya está conectado en setup_connect_button()
        # Botón para refrescar puertos COM (si existe)
        # self.ui.refreshPortsBtn.clicked.connect(self.populate_com_ports)
        
    def setup_title(self):
        """Configura el título de la página"""
        self.ui.label_11.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.label_11.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        
    def setup_com_port_selector(self):
        """Configura el selector de puerto COM"""
        # Label
        self.ui.label_21.setFont(QFont("Sitka Small", 10))
        self.ui.label_21.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        
        # ComboBox
        self.ui.comPort.setFont(QFont("Sitka Small", 10))
        self.ui.comPort.setStyleSheet("""
            QComboBox {
                background-color: THEME.COLOR_BACKGROUND_2;
                color: THEME.COLOR_TEXT_1;
                border: 2px solid THEME.COLOR_ACCENT_3;
                border-radius: 5px;
                padding: 8px;
                min-height: 30px;
            }
            QComboBox:hover {
                border: 2px solid THEME.COLOR_ACCENT_1;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(:/feather/icons/feather/chevron-down.png);
                width: 14px;
                height: 14px;
            }
            QComboBox QAbstractItemView {
                background-color: THEME.COLOR_BACKGROUND_2;
                color: THEME.COLOR_TEXT_1;
                selection-background-color: THEME.COLOR_ACCENT_2;
                border: 2px solid THEME.COLOR_ACCENT_3;
            }
        """)
        
        # Poblar con puertos disponibles
        self.populate_com_ports()
        
    def populate_com_ports(self):
        """Pobla el selector con los puertos COM disponibles"""
        self.ui.comPort.clear()
        
        # Obtener puertos disponibles
        available_ports = QSerialPortInfo.availablePorts()
        
        if available_ports:
            for port in available_ports:
                port_name = port.portName()
                port_description = port.description()
                display_text = f"{port_name} - {port_description}"
                self.ui.comPort.addItem(display_text, port_name)
        else:
            self.ui.comPort.addItem("No ports available", None)
            
    def setup_baud_rate_selector(self):
        """Configura el selector de baud rate"""
        # Label
        self.ui.label_22.setFont(QFont("Sitka Small", 10))
        self.ui.label_22.setStyleSheet("color: THEME.COLOR_TEXT_1;")
        
        # ComboBox
        self.ui.baudRate.setFont(QFont("Sitka Small", 10))
        self.ui.baudRate.setStyleSheet("""
            QComboBox {
                background-color: THEME.COLOR_BACKGROUND_2;
                color: THEME.COLOR_TEXT_1;
                border: 2px solid THEME.COLOR_ACCENT_3;
                border-radius: 5px;
                padding: 8px;
                min-height: 30px;
            }
            QComboBox:hover {
                border: 2px solid THEME.COLOR_ACCENT_1;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(:/feather/icons/feather/chevron-down.png);
                width: 14px;
                height: 14px;
            }
            QComboBox QAbstractItemView {
                background-color: THEME.COLOR_BACKGROUND_2;
                color: THEME.COLOR_TEXT_1;
                selection-background-color: THEME.COLOR_ACCENT_2;
                border: 2px solid THEME.COLOR_ACCENT_3;
            }
        """)
        
        # Poblar con baud rates comunes
        self.populate_baud_rates()
        
    def populate_baud_rates(self):
        """Pobla el selector con baud rates comunes"""
        self.ui.baudRate.clear()
        
        # Baud rates comunes
        baud_rates = [
            "9600",
            "19200",
            "38400",
            "57600",
            "115200",
            "230400",
            "460800",
            "921600"
        ]
        
        for rate in baud_rates:
            self.ui.baudRate.addItem(rate, int(rate))
            
        # Seleccionar 115200 por defecto (común para Arduino y dispositivos modernos)
        default_index = baud_rates.index("115200")
        self.ui.baudRate.setCurrentIndex(default_index)
        
    def setup_connect_button(self):
        """Configura el botón de conectar"""
        self.ui.connectBtn.setFont(QFont("Sitka Small", 11, QFont.Weight.Bold))
        self.ui.connectBtn.setMinimumHeight(50)
        self.ui.connectBtn.setCheckable(True)
        
        self.ui.connectBtn.setStyleSheet("""
            QPushButton {
                background-color: THEME.COLOR_BACKGROUND_2;
                color: THEME.COLOR_TEXT_1;
                border: 2px solid THEME.COLOR_ACCENT_3;
                border-radius: 10px;
                padding: 12px;
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
            QPushButton:checked:hover {
                background-color: #45a049;
            }
        """)
        
        # Conectar señal
        self.ui.connectBtn.clicked.connect(self.handle_connect_click)
        
    def handle_connect_click(self):
        """
        Maneja el clic del botón de conectar con el iSMC. La conexión se
        lanza en un QThread para no congelar la interfaz mientras se
        establece (o falla) la comunicación con el controlador.
        """
        if self.ui.connectBtn.isChecked():
            if self.controller.is_connected:
                self._on_connect_finished(True)
                return

            self.ui.connectBtn.setEnabled(False)
            self.ui.connectBtn.setText("Connecting...")

            self._connect_thread = QThread()
            self._connect_worker = _ConnectWorker(self.controller, "::1")
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
        else:
            print("[Aerotech] No se pudo conectar con el iSMC")
            self.ui.connectBtn.setChecked(False)
            self.ui.connectBtn.setText("Connect")