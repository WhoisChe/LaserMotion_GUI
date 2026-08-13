########################################################################
## GESTOR CENTRALIZADO DEL CONTROLADOR AEROTECH AUTOMATION1-iSMC
##
## Envuelve la API real del paquete "automation1" (SDK oficial de Aerotech)
## para que todas las páginas de la interfaz (Home, Manual, Auto, G-Code,
## Calibration) compartan una única conexión, en vez de que cada página
## intente abrir la suya o adivinar la de otra.
##
## El iSMC gestiona los drives iXC2e (eje X) y XC2e (ejes Y, Z) que mueven
## el ANT130XY y el ANT130LZS respectivamente.
########################################################################

import automation1 as a1

# Nombres de ejes tal como están configurados en el controlador
AXIS_X = "X"   # ANT130XY — Eje X
AXIS_Y = "Y"   # ANT130XY — Eje Y
AXIS_Z = "Z"   # ANT130LZS — Eje Z
AXES = (AXIS_X, AXIS_Y, AXIS_Z)


class AerotechController:
    """Envoltorio fino sobre la API automation1 para el controlador iSMC."""

    def __init__(self):
        self._controller = None
        self._status_config = None

    @property
    def is_connected(self):
        return self._controller is not None

    # ─────────────────────────────────────────────────────────────────
    # Conexión
    # ─────────────────────────────────────────────────────────────────
    def connect(self, host="192.168.7.1"):  
        """
        Conecta y arranca el controlador iSMC.
        host: "::1" (localhost) si la app corre en el mismo PC industrial
        que el controlador, o la IP del controlador si es remoto.
        Devuelve True si la conexión tuvo éxito.
        """
        try:
            self._controller = a1.Controller.connect(host=host)
            self._controller.start()

            # Configuración de los items de estado que se piden en cada
            # refresco (posición y estado de los drives de los 3 ejes)
            self._status_config = a1.StatusItemConfiguration()
            for axis in AXES:
                self._status_config.axis.add(a1.AxisStatusItem.PositionFeedback, axis)
                self._status_config.axis.add(a1.AxisStatusItem.DriveStatus, axis)

            print(f"[Aerotech] Conectado y arrancado correctamente (host={host})")
            return True
        except Exception as e:
            print(f"[Aerotech] Error al conectar al iSMC: {e}")
            self._controller = None
            self._status_config = None
            return False

    def disconnect(self):
        if self._controller is not None:
            try:
                self._controller.disconnect()
            except Exception as e:
                print(f"[Aerotech] Error al desconectar: {e}")
        self._controller = None
        self._status_config = None

    # ─────────────────────────────────────────────────────────────────
    # Estado / lectura
    # ─────────────────────────────────────────────────────────────────
    def get_axis_positions(self):
        """Devuelve (x, y, z) en mm, o (0.0, 0.0, 0.0) si no hay conexión."""
        if not self.is_connected:
            return 0.0, 0.0, 0.0
        try:
            results = self._controller.runtime.status.get_status_items(self._status_config)
            x = results.axis.get(a1.AxisStatusItem.PositionFeedback, AXIS_X).value
            y = results.axis.get(a1.AxisStatusItem.PositionFeedback, AXIS_Y).value
            z = results.axis.get(a1.AxisStatusItem.PositionFeedback, AXIS_Z).value
            return x, y, z
        except Exception as e:
            print(f"[Aerotech] Error leyendo posiciones: {e}")
            return 0.0, 0.0, 0.0

    def get_axes_enabled(self):
        """True si los tres ejes (X, Y, Z) están habilitados (drives activos)."""
        if not self.is_connected:
            return False
        try:
            results = self._controller.runtime.status.get_status_items(self._status_config)
            enabled_bit = int(a1.DriveStatus.Enabled)
            for axis in AXES:
                drive_status = int(results.axis.get(a1.AxisStatusItem.DriveStatus, axis).value)
                if not (drive_status & enabled_bit):
                    return False
            return True
        except Exception as e:
            print(f"[Aerotech] Error comprobando estado de los drives: {e}")
            return False

    # ─────────────────────────────────────────────────────────────────
    # Habilitación / homing
    # ─────────────────────────────────────────────────────────────────
    def enable_axes(self, axes=AXES):
        if not self.is_connected:
            return
        try:
            self._controller.runtime.commands.motion.enable(list(axes))
            print(f"[Aerotech] Ejes {list(axes)} habilitados")
        except Exception as e:
            print(f"[Aerotech] Error habilitando ejes: {e}")

    def disable_axes(self, axes=AXES):
        if not self.is_connected:
            return
        try:
            self._controller.runtime.commands.motion.disable(list(axes))
            print(f"[Aerotech] Ejes {list(axes)} deshabilitados")
        except Exception as e:
            print(f"[Aerotech] Error deshabilitando ejes: {e}")

    def home_axes(self, axes=AXES):
        """
        Ejecuta el homing de los ejes indicados.
        ATENCIÓN: MotionCommands.home() es una llamada BLOQUEANTE (espera a
        que termine el ciclo de homing), así que congela la interfaz mientras
        dura. Para producción, lanzar esto desde un QThread/worker en vez de
        desde el hilo de la UI.
        """
        if not self.is_connected:
            return
        try:
            self._controller.runtime.commands.motion.home(list(axes))
            print(f"[Aerotech] Homing completado en ejes {list(axes)}")
        except Exception as e:
            print(f"[Aerotech] Error en homing: {e}")

    # ─────────────────────────────────────────────────────────────────
    # Movimiento
    # ─────────────────────────────────────────────────────────────────
    def _set_acceleration(self, axis, acceleration):
        """Aplica la misma rampa de aceleración/deceleración (mm/s²) a un eje."""
        self._controller.runtime.commands.motion_setup.setupaxisrampvalue(
            axis, a1.RampMode.Rate, acceleration, a1.RampMode.Rate, acceleration
        )

    def move_relative(self, axis, distance_mm, velocity, acceleration):
        """Mueve un único eje una distancia relativa (mm)."""
        if not self.is_connected:
            print(f"[Aerotech] Sin conexión — movimiento {axis} ignorado")
            return
        try:
            self._set_acceleration(axis, acceleration)
            self._controller.runtime.commands.motion.moveincremental([axis], [distance_mm], [velocity])
            print(f"[Aerotech] {axis} -> {distance_mm:+.4f} mm @ {velocity} mm/s (acc {acceleration} mm/s²)")
        except Exception as e:
            print(f"[Aerotech] Error en movimiento relativo {axis}: {e}")

    def move_incremental(self, axes, distances, velocity, acceleration):
        """Mueve varios ejes una distancia relativa (mm) cada uno, misma velocidad/aceleración para todos."""
        if not self.is_connected:
            print("[Aerotech] Sin conexión — movimiento incremental ignorado")
            return
        try:
            axes = list(axes)
            distances = list(distances)
            for axis in axes:
                self._set_acceleration(axis, acceleration)
            speeds = [velocity] * len(axes)
            self._controller.runtime.commands.motion.moveincremental(axes, distances, speeds)
            print(f"[Aerotech] Movimiento incremental enviado -> {dict(zip(axes, distances))}")
        except Exception as e:
            print(f"[Aerotech] Error en movimiento incremental: {e}")

    def move_absolute(self, axes, positions, velocity, acceleration):
        """Mueve varios ejes a una posición absoluta (mm), misma velocidad/aceleración para todos."""
        if not self.is_connected:
            print("[Aerotech] Sin conexión — movimiento absoluto ignorado")
            return
        try:
            axes = list(axes)
            positions = list(positions)
            for axis in axes:
                self._set_acceleration(axis, acceleration)
            speeds = [velocity] * len(axes)
            self._controller.runtime.commands.motion.moveabsolute(axes, positions, speeds)
            print(f"[Aerotech] Movimiento absoluto enviado -> {dict(zip(axes, positions))}")
        except Exception as e:
            print(f"[Aerotech] Error en movimiento absoluto: {e}")

    def zero_axis(self, axis, value=0.0):
        """
        Establece la posición actual del eje como el valor indicado (por
        defecto 0), sin mover el eje físicamente (desplaza el origen de
        coordenadas del programa).
        """
        if not self.is_connected:
            print(f"[Aerotech] Sin conexión — no se puede fijar el origen del eje {axis}")
            return
        try:
            self._controller.runtime.commands.motion.positionoffsetset([axis], [value])
            print(f"[Aerotech] Eje {axis} fijado a {value} mm en la posición actual")
        except Exception as e:
            print(f"[Aerotech] Error fijando el origen del eje {axis}: {e}")

    # ─────────────────────────────────────────────────────────────────
    # E/S digital (usado, por ejemplo, para el shutter del láser)
    # ─────────────────────────────────────────────────────────────────
    def set_digital_output(self, axis, output_num, value):
        """
        Activa/desactiva una salida digital del drive de "axis" (p. ej. el
        shutter del láser). "output_num" depende del cableado real de la
        estación y debe ajustarse a como esté conectado en el laboratorio.
        """
        if not self.is_connected:
            print("[Aerotech] Sin conexión — salida digital ignorada")
            return
        try:
            self._controller.runtime.commands.io.digitaloutputset(axis, output_num, int(value))
            print(f"[Aerotech] Salida digital {output_num} (eje {axis}) -> {int(value)}")
        except Exception as e:
            print(f"[Aerotech] Error escribiendo salida digital: {e}")
