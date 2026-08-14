"""
================================================================================
 Script de verificacion del sistema de nanoposicionamiento Aerotech
 Pedido 644118-1-1 - Universidad de Salamanca
 Ejes: X (iXC2e) - Y (XC2e) - Z (XC2e) | Etapas ANT130XY + ANT130LZS
================================================================================

QUE HACE ESTE SCRIPT
Usa la API de Python de Automation1 para:
  1. Conectarse al controlador y comprobar que arranca correctamente.
  2. Leer el estado de cada eje (habilitado, referenciado/homed, en posicion,
     fallos activos) SIN mover nada.
  3. (Opcional, con confirmacion explicita) Habilitar, referenciar (home) y
     hacer un movimiento pequeno de prueba en cada eje, uno a uno.
  4. Dejar el sistema en un estado seguro al terminar (ejes deshabilitados y
     controlador desconectado), incluso si algo falla a mitad del script.

ANTES DE EJECUTARLO
  - El sistema debe estar cableado y comisionado (24 VDC y 80 VDC en los
    tres drives, HyperWire conectado, PC conectado al iXC2e por USB o
    Ethernet, Automation1-iSMC en marcha).
  - Mantienes el bypass de STO, es decir, los ejes se habilitaran SIN ningun
    paro de emergencia por hardware de por medio: antes de decir "s" a la
    parte de movimiento, ten la mano lista para cortar la alimentacion de
    motor si algo no va como esperas.
  - Despeja la zona de recorrido de los tres ejes antes de la parte de
    movimiento.
  - Este script asume que los ejes se llaman 'X', 'Y' y 'Z' en Automation1
    (coincide con Eje 1/2/3 de tu hoja de especificaciones). Si en
    Automation1 Studio > Configuration > Axes tienen otro nombre, cambia la
    lista AXES mas abajo.

INSTALACION DEL ENTORNO (una sola vez, en la terminal integrada de VSCode)
  1. Instala Automation1-MDK si no lo tienes (incluye la API de Python).
  2. Dentro de tu entorno virtual de Python, instala el paquete local:
       pip install automation1 --find-links="C:\\Program Files\\Aerotech\\Automation1-MDK\\APIs\\Python" --no-index
     (ajusta la ruta si instalaste Automation1-MDK en otro sitio)
  3. La version de la API de Python debe coincidir con la version del
     controlador Automation1 que tengas instalada; si no coinciden, la
     conexion falla.

SOBRE LO QUE ESTA VERIFICADO Y LO QUE ES UNA ESTIMACION
Las llamadas de conexion, arranque, habilitacion, home y movimiento
(Controller.connect, start, is_running, runtime.commands.motion.enable/home/
movelinear) estan tomadas literalmente del ejemplo oficial de Aerotech
("Use the Automation1 Python API in a Jupyter Notebook"). La funcion
comprobar_estado_ejes() esta construida por analogia con la API de
AeroScript/C (que si confirma los nombres AxisStatusItem, AxisStatus,
DriveStatus), pero no he podido verificar al 100% la sintaxis exacta de
recuperacion de resultados de estado en Python. Por eso esa funcion esta
aislada con su propio manejo de errores: si falla, el resto del script no
se ve afectado. Si falla, tienes ejemplos ya probados y con la sintaxis
exacta de tu version instalada en:
  C:\\Program Files\\Aerotech\\Automation1-MDK\\Examples\\Python
================================================================================
"""

import time

import automation1 as a1

# ------------------------------------------------------------------
# CONFIGURACION - ajusta esto a tu sistema si hace falta
# ------------------------------------------------------------------
AXES = ['X', 'Y', 'Z']       # Nombres de eje configurados en Automation1
TEST_DISTANCE_MM = 0.01      # Movimiento de prueba: 10 micras
TEST_SPEED_MM_S = 1.0        # Muy por debajo del maximo de tu sistema (100 mm/s)


def conectar_y_arrancar():
    """Conecta con el controlador Automation1 local y lo arranca si hace falta."""
    print("\n[1/5] Conectando con el controlador Automation1...")
    controller = a1.Controller.connect()
    if not controller.is_running:
        controller.start()
    if controller.is_running:
        print("      OK - Controlador conectado y en marcha.")
    else:
        print("      FALLO - El controlador no ha arrancado.")
    return controller


def comprobar_estado_ejes(controller, axes):
    """
    Intenta leer el estado (habilitado / referenciado / en posicion / fallo)
    de cada eje sin mover nada. Ver la nota de cabecera sobre el nivel de
    confianza de esta funcion en concreto.
    """
    print("\n      Leyendo estado de los ejes (sin mover nada)...")
    try:
        status_config = a1.StatusItemConfiguration()
        for axis in axes:
            status_config.axis.add(a1.AxisStatusItem.AxisStatus, axis)
            status_config.axis.add(a1.AxisStatusItem.DriveStatus, axis)
            status_config.axis.add(a1.AxisStatusItem.AxisFault, axis)
            status_config.axis.add(a1.AxisStatusItem.PositionFeedback, axis)

        results = controller.runtime.status.get_status_items(status_config)

        for axis in axes:
            axis_status = int(results.axis.get(a1.AxisStatusItem.AxisStatus, axis).value)
            drive_status = int(results.axis.get(a1.AxisStatusItem.DriveStatus, axis).value)
            axis_fault = int(results.axis.get(a1.AxisStatusItem.AxisFault, axis).value)
            position = results.axis.get(a1.AxisStatusItem.PositionFeedback, axis).value

            homed = bool(axis_status & a1.AxisStatus.Homed)
            enabled = bool(drive_status & a1.DriveStatus.Enabled)
            in_position = bool(drive_status & a1.DriveStatus.InPosition)
            con_fallo = axis_fault != 0

            estado_fallo = f"CON FALLO (bitmask={axis_fault})" if con_fallo else "sin fallo"
            print(f"      Eje {axis}: posicion={position:.4f} mm | "
                  f"habilitado={enabled} | referenciado={homed} | "
                  f"en posicion={in_position} | {estado_fallo}")

    except AttributeError as e:
        print(f"      No se ha podido leer el estado con esta sintaxis ({e}). "
              "Revisa la referencia local de la API de Python instalada "
              "(carpeta APIs\\Python) o los ejemplos en Examples\\Python "
              "para la sintaxis exacta de tu version. El resto del script "
              "no depende de esta funcion.")
    except a1.ControllerException as e:
        print(f"      El controlador ha devuelto un error al leer estado: {e}")


def habilitar_y_referenciar(controller, axis):
    """Habilita un eje y lo referencia (home). Devuelve True si todo ha ido bien."""
    try:
        print(f"\n      Habilitando eje {axis}...")
        controller.runtime.commands.motion.enable([axis])
        print(f"      Referenciando (home) eje {axis}...")
        controller.runtime.commands.motion.home([axis])
        print(f"      OK - Eje {axis} habilitado y referenciado.")
        return True
    except a1.ControllerException as e:
        print(f"      FALLO en eje {axis}: {e}")
        return False


def movimiento_de_prueba(controller, axis, distancia_mm, velocidad_mm_s):
    """Hace un movimiento lineal pequeno de ida y vuelta en un eje."""
    try:
        print(f"      Moviendo eje {axis} +{distancia_mm} mm a {velocidad_mm_s} mm/s...")
        controller.runtime.commands.motion.movelinear(axis, [distancia_mm], velocidad_mm_s)
        time.sleep(0.5)
        print(f"      Volviendo eje {axis} a la posicion inicial...")
        controller.runtime.commands.motion.movelinear(axis, [-distancia_mm], velocidad_mm_s)
        print(f"      OK - Movimiento de prueba del eje {axis} completado.")
        return True
    except a1.ControllerException as e:
        print(f"      FALLO en el movimiento del eje {axis}: {e}")
        return False


def deshabilitar_ejes(controller, axes):
    """Deshabilita los ejes indicados (estado seguro de reposo)."""
    try:
        controller.runtime.commands.motion.disable(axes)
        print("      Ejes deshabilitados.")
    except a1.ControllerException as e:
        print(f"      Aviso: no se han podido deshabilitar los ejes limpiamente: {e}")


def main():
    controller = None
    try:
        controller = conectar_y_arrancar()
        if not controller.is_running:
            print("\nEl controlador no esta en marcha; revisa Automation1 Studio antes de continuar.")
            return

        comprobar_estado_ejes(controller, AXES)

        respuesta = input(
            "\n[2/5] Zona despejada y listo para mover ejes de verdad? "
            "Se habilitara, referenciara y movera cada eje una pequena "
            "distancia de prueba. (s/n): "
        ).strip().lower()

        if respuesta == 's':
            print("\n[3/5] Probando cada eje...")
            for axis in AXES:
                print(f"\n--- Eje {axis} ---")
                if habilitar_y_referenciar(controller, axis):
                    mover = input(
                        f"      Hacer el movimiento de prueba de "
                        f"{TEST_DISTANCE_MM} mm en el eje {axis}? (s/n): "
                    ).strip().lower()
                    if mover == 's':
                        movimiento_de_prueba(controller, axis, TEST_DISTANCE_MM, TEST_SPEED_MM_S)

            print("\n[4/5] Releyendo estado tras las pruebas de movimiento...")
            comprobar_estado_ejes(controller, AXES)

            deshabilitar_ejes(controller, AXES)
        else:
            print("\nSaltando la parte de movimiento; solo se ha comprobado conexion y estado.")

        print("\n[5/5] Prueba finalizada.")

    except a1.ControllerException as e:
        print(f"\nError del controlador Automation1: {e}")
    except Exception as e:
        print(f"\nError inesperado: {e}")
    finally:
        if controller is not None:
            try:
                deshabilitar_ejes(controller, AXES)
            except Exception:
                pass
            try:
                controller.disconnect()
                print("Desconectado del controlador.")
            except Exception:
                pass


if __name__ == "__main__":
    main()