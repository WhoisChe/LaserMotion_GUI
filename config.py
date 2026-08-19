########################################################################
## CONFIGURACIÓN GLOBAL DEL PROYECTO
########################################################################

# Indica si la señal de interlock del láser está disponible y cableada en
# el interconnect real de la estación. Mientras esté en False, el LED de
# interlock de la página Home se muestra en gris fijo ("Interlock: N/D").
# Cuando se confirme la señal en el documento 620D1426-10-01 System
# Interconnect, cambiar a True y conectar la lectura real en
# AerotechController — no debería requerir tocar nada más en
# src/ui_extensions_home.py aparte de leer este flag.
LASER_INTERLOCK_AVAILABLE = False

# Indica si el cable Dual-PSO Adapter (ECZ03125-3) entre Drive 1 y Drive 2
# está confirmado como mecanismo funcional de disparo PSO de dos ejes
# (necesario para pasadas diagonales en "Point array" de Auto). Pendiente de
# verificación en laboratorio — ver 00_global_architecture.md §3.
SYNC_PORTS_AVAILABLE = False

# Aceleración fija por eje (mm/s²), usada por Manual/Auto ahora que la
# aceleración ya no es un control visible en la interfaz (antes era un
# QDoubleSpinBox editable en Manual). Ajustar según las capacidades reales
# de cada mesa (ANT130XY-060 para X/Y, ANT130LZS-035 para Z).
DEFAULT_ACCELERATION_MM_S2 = {"X": 100.0, "Y": 100.0, "Z": 100.0}

# Tope de potencia (%) forzado por "Laser alignment mode" en Calibration —
# suficiente para ver el punto del láser sin quemar/marcar la pieza mientras
# se alinea. Ajustar según sensibilidad del material usado en el laboratorio.
ALIGNMENT_MODE_MAX_POWER_PERCENT = 8
