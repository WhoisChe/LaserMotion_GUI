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
