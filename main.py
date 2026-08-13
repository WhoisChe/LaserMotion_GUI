########################################################################
## INTERFAZ GUI ESTACIÓN LÁSER
#C:\Users\dasag\Desktop\Automation1\PyQt6_CodeOnly>venv\Scripts\activate
#prueba
########################################################################

import os
import sys

# Importar el archivo GUI 
from src.ui_interface import *

# Importar Custom widgets
from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings

# Importar funciones para los botones del menú, aplicación de temas, y fuente.
from src.Functions import GuiFunctions

# Importar archivo de extensiones para modificar el diseño
from src.ui_extensions import UIExtensions

########################################################################
## MAIN WINDOW CLASS
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Especifica la direccion/nombre del archivo json
        loadJsonStyle(self, self.ui, jsonFiles = {
            "json-styles/style.json"
        }) 

        # Aplicar modificaciones de ui_extensions
        self.ui_ext = UIExtensions(self.ui, self)
        self.ui_ext.apply_all_modifications()
        
        # Conectar todas las señales
        self.ui_ext.connect_all_signals()

        # La conexión con el controlador Aerotech Automation1-iSMC se
        # gestiona de forma centralizada en UIExtensions (ver
        # src/ui_extensions.py y src/aerotech_controller.py), ya invocada
        # dentro de self.ui_ext.apply_all_modifications() más arriba.

        # Muestra la ventana principal
        self.show()

        # Actualiza configuración de la app
        QAppSettings.updateAppSettings(self)

        # Aplica funciones y eventos
        self.app_functions = GuiFunctions(self)

########################################################################
## EXECUTE APP
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
########################################################################
## END

