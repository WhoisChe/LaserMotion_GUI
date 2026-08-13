"""
Prueba basica de conexion con el controlador Aerotech Automation1-iSMC
(drives iXC2e/XC2e, ejes X/Y/Z).

Solo hace lo minimo:
  1. Conecta al controlador.
  2. Lee y muestra la posicion de cada eje.
  3. Si el usuario confirma, mueve UN eje 0.01 mm y vuelve.
  4. Desconecta.

Requiere el paquete "automation1" ya instalado en el entorno (ver test.py
para las instrucciones de instalacion si no lo tienes).
"""
# Carga la librería aerotech y le pone alias a1
import automation1 as a1

# Nombra las variables
HOST = "192.168.7.1"          # IP del controlador
AXES = ["X", "Y", "Z"]
EJE_DE_PRUEBA = "X"
DISTANCIA_MM = 0.01
VELOCIDAD_MM_S = 1.0


def main():
    print(f"Conectando al controlador Automation1 (host={HOST})...")
    # Conexión: abre la comunicación con el controlador y lo arranca
    controller = a1.Controller.connect(host=HOST)
    controller.start()
    print("Conectado y arrancado.")

    try:
        # Lee la posición de cada eje
        status_config = a1.StatusItemConfiguration()
        for axis in AXES:
            status_config.axis.add(a1.AxisStatusItem.PositionFeedback, axis)

        # Da el valor de posición de cada eje
        results = controller.runtime.status.get_status_items(status_config)
        for axis in AXES:
            pos = results.axis.get(a1.AxisStatusItem.PositionFeedback, axis).value
            print(f"  Eje {axis}: {pos:.4f} mm")

        # Pregunta si mueve un eje
        respuesta = input(
            f"\nMover el eje {EJE_DE_PRUEBA} {DISTANCIA_MM} mm y volver? (s/n): "
        ).strip().lower()

        if respuesta == "s":
            controller.runtime.commands.motion.enable([EJE_DE_PRUEBA])  # Activa el motor
            controller.runtime.commands.motion.home([EJE_DE_PRUEBA])    # Hace el homing
            controller.runtime.commands.motion.movelinear(
                EJE_DE_PRUEBA, [DISTANCIA_MM], VELOCIDAD_MM_S
            )
            controller.runtime.commands.motion.movelinear(
                EJE_DE_PRUEBA, [-DISTANCIA_MM], VELOCIDAD_MM_S          # Mueve el eje hacia una dirección (a una distancia y velocidad) y luego en sentido contrario
            )
            controller.runtime.commands.motion.disable([EJE_DE_PRUEBA]) # Desactiva el momtor
            print("Movimiento de prueba completado.")
        else:
            print("Movimiento omitido.")

    finally:
        controller.disconnect()
        print("Desconectado.")


if __name__ == "__main__":
    main()
