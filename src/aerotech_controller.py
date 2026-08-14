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

# Potencia máxima del módulo láser NEJE B30635 (mW), usada para convertir el
# duty cycle (%) de la consigna a una potencia estimada en mW.
NEJE_B30635_MAX_POWER_MW = 500.0


class AerotechController:
    """Envoltorio fino sobre la API automation1 para el controlador iSMC."""

    def __init__(self):
        self._controller = None
        self._status_config = None
        self._host = None
        # Consigna de potencia del láser (0-100%), aplicada por software con
        # set_laser_power_percent(). Ver comentario de esa función: hasta que
        # se confirme el canal PWM real, no se escribe sobre ninguna salida.
        self._laser_duty_cycle = 0.0

    @property
    def is_connected(self):
        return self._controller is not None

    @property
    def host(self):
        """Host/IP del último intento de conexión (None si nunca se ha conectado)."""
        return self._host

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
            self._host = host

            # Configuración de los items de estado que se piden en cada
            # refresco (posición, estado de los drives y fallos de los 3 ejes)
            self._status_config = a1.StatusItemConfiguration()
            for axis in AXES:
                self._status_config.axis.add(a1.AxisStatusItem.PositionFeedback, axis)
                self._status_config.axis.add(a1.AxisStatusItem.DriveStatus, axis)
                self._status_config.axis.add(a1.AxisStatusItem.AxisFault, axis)

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

    def get_axis_faults(self):
        """
        Descompone el bitmask de AxisFault de cada eje en banderas legibles.
        Devuelve {axis: {"position_error": bool, "limit_cw": bool, "limit_ccw": bool}}.
        Si no hay conexión, todas las banderas vuelven False para los 3 ejes.
        """
        # TODO: verificar nombres exactos de los bits contra a1.AxisFault en
        # la instalación real (dir(a1.AxisFault)) — no asumir nombres de bit
        # sin esa verificación.
        empty = {"position_error": False, "limit_cw": False, "limit_ccw": False}
        if not self.is_connected:
            return {axis: dict(empty) for axis in AXES}
        try:
            results = self._controller.runtime.status.get_status_items(self._status_config)
            faults = {}
            for axis in AXES:
                fault_bits = int(results.axis.get(a1.AxisStatusItem.AxisFault, axis).value)
                faults[axis] = {
                    "position_error": bool(fault_bits & int(a1.AxisFault.PositionErrorFault)),
                    "limit_cw": bool(fault_bits & int(a1.AxisFault.CwEndOfTravelLimitFault)),
                    "limit_ccw": bool(fault_bits & int(a1.AxisFault.CcwEndOfTravelLimitFault)),
                }
            return faults
        except Exception as e:
            print(f"[Aerotech] Error leyendo fallos de eje: {e}")
            return {axis: dict(empty) for axis in AXES}

    def get_axes_homed(self):
        """True/False por eje según el bit de homed dentro de DriveStatus."""
        # TODO: verificar el nombre exacto del bit de homed contra
        # a1.DriveStatus en la instalación real (dir(a1.DriveStatus)).
        if not self.is_connected:
            return {axis: False for axis in AXES}
        try:
            results = self._controller.runtime.status.get_status_items(self._status_config)
            homed_bit = int(a1.DriveStatus.Homed)
            homed = {}
            for axis in AXES:
                drive_status = int(results.axis.get(a1.AxisStatusItem.DriveStatus, axis).value)
                homed[axis] = bool(drive_status & homed_bit)
            return homed
        except Exception as e:
            print(f"[Aerotech] Error comprobando estado de homing: {e}")
            return {axis: False for axis in AXES}

    def get_sto_status(self, axis=None):
        """
        True si el STO (Safe Torque Off) está activo. Si "axis" es None, hace
        OR del estado de todos los ejes; si se pasa un eje, solo el suyo.
        """
        # TODO: puede ser un bit dentro de AxisFault o un status item de
        # sistema aparte, depende de cómo esté cableada la cadena de
        # seguridad en HyperWire — dejar preparado para ambos casos hasta
        # confirmar con el documento de interconexión (620D1426-10-01).
        if not self.is_connected:
            return False
        try:
            results = self._controller.runtime.status.get_status_items(self._status_config)
            sto_bit = int(a1.AxisFault.StoFault) if hasattr(a1.AxisFault, "StoFault") else 0
            if sto_bit == 0:
                return False
            axes_to_check = (axis,) if axis is not None else AXES
            for ax in axes_to_check:
                fault_bits = int(results.axis.get(a1.AxisStatusItem.AxisFault, ax).value)
                if fault_bits & sto_bit:
                    return True
            return False
        except Exception as e:
            print(f"[Aerotech] Error comprobando estado de STO: {e}")
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

    # ─────────────────────────────────────────────────────────────────
    # Salida de potencia del láser (PWM) — ver NEJE_B30635_MAX_POWER_MW
    # ─────────────────────────────────────────────────────────────────
    def set_laser_power_percent(self, duty_percent: float):
        """
        Fija la consigna de duty cycle del láser (0-100%).

        El canal PWM físico todavía no está confirmado (falta el documento
        620D1426-10-01 System Interconnect para saber a qué eje/salida está
        cableado el pin TTL/PWM del NEJE), así que por ahora esta función NO
        escribe sobre ninguna salida real: solo guarda el valor y avisa por
        consola que está en modo simulado. Cuando se confirme el canal físico,
        esta función pasará a escribir también sobre el output real.
        """
        self._laser_duty_cycle = duty_percent
        print(f"[Aerotech] (modo simulado) Consigna de potencia láser -> {duty_percent:.0f}% "
              f"— canal PWM real aún no confirmado, no se escribe salida física")

    def get_laser_output_state(self):
        """Devuelve (is_on, duty_percent, power_mw) según la última consigna guardada."""
        duty_percent = self._laser_duty_cycle
        power_mw = duty_percent / 100 * NEJE_B30635_MAX_POWER_MW
        is_on = duty_percent > 0
        return is_on, duty_percent, power_mw
