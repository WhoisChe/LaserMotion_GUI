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

# Cableado físico confirmado (ver 07_laser_hardware_integration.md):
# - PSO pin 3/4 (TTL/PWM + GND) del drive 1/iXC2e va al pin TTL de la placa
#   adaptadora del NEJE B30635 -> eje X.
# - Digital Output [-EB1] "Output 1" del mismo drive controla el relé (activo
#   en alto) que alimenta esa placa adaptadora (Input B, PWR/GND/TTL).
#   Verificado en el laboratorio: con el eje habilitado, DigitalOutputSet(X,
#   1, 1) + PsoOutputOn(X) es la secuencia que realmente dispara el láser.
PSO_LASER_AXIS = AXIS_X
RELAY_CONTROL_AXIS = AXIS_X
RELAY_OUTPUT_NUM = 1


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
        # Último error de get_axis_indicators() (None si la última lectura
        # fue correcta) — permite a la interfaz mostrar un aviso visible en
        # pantalla en vez de que el fallo quede solo en la consola.
        self._indicator_error = None
        # Último error de cualquier método pso_* (None si la última llamada
        # fue correcta) — pensado originalmente para nombres de
        # runtime.commands.pso.* sin confirmar (ya confirmados, ver sección
        # PSO más abajo), pero se mantiene: cualquier otro fallo real de
        # PSO tampoco debe pasar desapercibido con solo un print().
        self._pso_error = None

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
                self._status_config.axis.add(a1.AxisStatusItem.AxisStatus, axis)
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

    def get_axis_indicators(self, axis):
        """
        Estado combinado de un único eje para los 3 LEDs del panel global
        (Enabled/Homed/CW-CCW). Devuelve {"enabled": bool, "homed": bool,
        "limit_active": bool}; todo False si no hay conexión. Sustituye a
        las antiguas get_axes_enabled()/get_axes_homed()/get_axis_faults(),
        que devolvían un booleano combinado para los 3 ejes en el caso de
        "enabled" — aquí cada eje se lee de forma independiente.

        Nombres verificados contra dir(a1.DriveStatus)/dir(a1.AxisStatus)/
        dir(a1.AxisFault) con el paquete automation1 instalado: "Homed" NO
        existe en DriveStatus (de ahí que los LEDs no cambiaran nunca — la
        excepción se tragaba en silencio) — vive en AxisStatus, un status
        item aparte del eje, añadido a _status_config en connect().
        "Enabled" sí está en DriveStatus, y CwEndOfTravelLimitFault/
        CcwEndOfTravelLimitFault sí están en AxisFault; esos tres no cambian.
        """
        empty = {"enabled": False, "homed": False, "limit_active": False}
        if not self.is_connected:
            return dict(empty)
        try:
            results = self._controller.runtime.status.get_status_items(self._status_config)
            drive_status = int(results.axis.get(a1.AxisStatusItem.DriveStatus, axis).value)
            axis_status = int(results.axis.get(a1.AxisStatusItem.AxisStatus, axis).value)
            fault_bits = int(results.axis.get(a1.AxisStatusItem.AxisFault, axis).value)

            enabled = bool(drive_status & int(a1.DriveStatus.Enabled))
            homed = bool(axis_status & int(a1.AxisStatus.Homed))
            limit_active = bool(fault_bits & int(a1.AxisFault.CwEndOfTravelLimitFault)) or \
                bool(fault_bits & int(a1.AxisFault.CcwEndOfTravelLimitFault))

            self._indicator_error = None
            return {
                "enabled": enabled,
                "homed": homed,
                "limit_active": limit_active,
            }
        except Exception as e:
            print(f"[Aerotech] Error leyendo indicadores del eje {axis}: {e}")
            self._indicator_error = f"Axis indicators unavailable ({axis}): {e}"
            return dict(empty)

    def get_last_indicator_error(self):
        """Último error de get_axis_indicators(), o None si la última lectura
        fue correcta — para que la interfaz muestre un aviso visible."""
        return self._indicator_error

    def get_last_pso_error(self):
        """Último error de cualquier método pso_* (reset/output_on/output_off/
        configure_*), o None si la última llamada fue correcta — para que la
        interfaz muestre un aviso visible en vez de que un nombre de método
        equivocado quede solo en la consola."""
        return self._pso_error

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

    def set_laser_board_power(self, enabled: bool):
        """
        Cierra/abre el relé que alimenta la placa adaptadora del NEJE B30635
        (Digital Output [-EB1], Output 1). Con el relé abierto, el láser no
        puede emitir aunque se le mande PWM por PSO.

        Polaridad verificada en el laboratorio: el módulo de relé es activo en
        alto (IN a 5V cierra el contacto NO y alimenta la placa adaptadora),
        así que value=True -> relé cerrado es correcto tal cual, sin invertir.
        """
        self.set_digital_output(RELAY_CONTROL_AXIS, RELAY_OUTPUT_NUM, enabled)

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
        """
        Devuelve (is_on, duty_percent, power_mw, is_measured) según la última
        consigna guardada (self._laser_duty_cycle, actualizada tanto por
        set_laser_power_percent() como por pso_configure_waveform()).
        """
        # TODO: intentar leer el bit OutputActive real del estado de PSO
        # cuando se confirme el status item correspondiente; hasta entonces
        # is_measured siempre cae al fallback (False).
        is_measured = False
        duty_percent = self._laser_duty_cycle
        power_mw = duty_percent / 100 * NEJE_B30635_MAX_POWER_MW
        is_on = duty_percent > 0
        return is_on, duty_percent, power_mw, is_measured

    # ─────────────────────────────────────────────────────────────────
    # PSO (Position Synchronized Output) — salida dedicada del láser NEJE
    # B30635, cableada a la salida PSO del drive 1 / eje X (PSO_LASER_AXIS).
    #
    # Nombres confirmados contra dir(controller.runtime.commands.pso) en la
    # instalación real (ya no son hipótesis): todo en minúsculas, sin guion
    # bajo, nombre de AeroScript tal cual (PsoOutputOn -> psooutputon), igual
    # que motion/io. No existe una función única de "configurar Waveform":
    # hacen falta varias llamadas encadenadas (ver pso_configure_waveform).
    # Si algún enum (PsoWaveformMode, PsoOutputSource, PsoEventMask) no
    # existe con ese nombre exacto en esta instalación, no estaba en la
    # lista de dir() (que solo cubre funciones, no enums) — confirmar con
    # dir(a1) / dir(a1.PsoWaveformMode) contra hardware real antes de fiarse.
    # ─────────────────────────────────────────────────────────────────
    def pso_reset(self, axis=PSO_LASER_AXIS):
        """Reinicia la configuración PSO del eje antes de reconfigurarla."""
        if not self.is_connected:
            return
        try:
            self._controller.runtime.commands.pso.psoreset(axis)
            print(f"[Aerotech] PSO reset -> eje {axis}")
            self._pso_error = None
        except Exception as e:
            print(f"[Aerotech] Error en pso_reset({axis}): {e}")
            self._pso_error = f"PSO reset failed ({axis}): {e}"

    def pso_configure_fixed_distance(self, axis=PSO_LASER_AXIS, distance_mm=0.0):
        """Configura un evento PSO cada distance_mm recorridos por el eje."""
        if not self.is_connected:
            return
        try:
            pso = self._controller.runtime.commands.pso
            pso.psodistanceconfigurefixeddistance(axis, distance_mm)
            pso.psodistancecounteron(axis)
            pso.psodistanceeventson(axis)
            print(f"[Aerotech] PSO distancia fija -> eje {axis}, {distance_mm} mm")
            self._pso_error = None
        except Exception as e:
            print(f"[Aerotech] Error en pso_configure_fixed_distance({axis}): {e}")
            self._pso_error = f"PSO fixed distance failed ({axis}): {e}"

    def pso_configure_array_distances(self, axis=PSO_LASER_AXIS, distances_mm: list = None):
        """Configura un array de eventos PSO en distancias irregulares/no
        uniformes. Sin uso real actualmente (Point array ya no usa espaciado
        irregular) — nombre corregido igualmente por consistencia, pero sin
        probar todavía contra hardware."""
        if not self.is_connected:
            return
        distances_mm = distances_mm or []
        try:
            self._controller.runtime.commands.pso.psodistanceconfigurearraydistances(axis, list(distances_mm))
            print(f"[Aerotech] PSO array -> eje {axis}, {len(distances_mm)} distancias")
            self._pso_error = None
        except Exception as e:
            print(f"[Aerotech] Error en pso_configure_array_distances({axis}): {e}")
            self._pso_error = f"PSO array distances failed ({axis}): {e}"

    def pso_configure_waveform(self, axis=PSO_LASER_AXIS, power_percent=0.0, total_time_us=20000, pulse_count=1):
        """
        Configura el pulso PSO por evento cuyo ancho codifica la potencia
        (0-100%) del láser: on_time_us = total_time_us * power_percent / 100.
        También actualiza self._laser_duty_cycle, para que
        get_laser_output_state() refleje esta consigna (mismo almacén que
        usaba set_laser_power_percent(), ahora ya no llamado desde Manual).

        No hay una única llamada de "configurar Waveform": modo, tiempo
        total, tiempo de encendido y número de pulsos se fijan por separado
        y se aplican con psowaveformapplypulseconfiguration(), y la salida
        PSO debe apuntarse explícitamente a la fuente Waveform antes de
        encenderla con psowaveformon().
        """
        if not self.is_connected:
            return
        on_time_us = total_time_us * power_percent / 100
        try:
            pso = self._controller.runtime.commands.pso
            pso.psowaveformconfiguremode(axis, a1.PsoWaveformMode.Pulse)
            pso.psowaveformconfigurepulsefixedtotaltime(axis, total_time_us)
            pso.psowaveformconfigurepulsefixedontime(axis, on_time_us)
            pso.psowaveformconfigurepulsefixedcount(axis, pulse_count)
            pso.psowaveformapplypulseconfiguration(axis)
            pso.psooutputconfiguresource(axis, a1.PsoOutputSource.Waveform)
            pso.psowaveformon(axis)
            print(f"[Aerotech] PSO waveform -> eje {axis}, {power_percent:.0f}% "
                  f"({on_time_us:.0f}/{total_time_us} µs, {pulse_count} pulso(s))")
            self._laser_duty_cycle = power_percent
            self._pso_error = None
        except Exception as e:
            print(f"[Aerotech] Error en pso_configure_waveform({axis}): {e}")
            self._pso_error = f"PSO waveform failed ({axis}): {e}"

    def pso_configure_window(self, axis=PSO_LASER_AXIS, window_number=1, min_mm=0.0, max_mm=0.0, as_mask: bool = False):
        """Configura una ventana PSO (rango de posición en el que puede
        disparar). as_mask enmascara los eventos PSO dentro de la ventana en
        vez de conmutar la salida directamente sobre WindowOutput."""
        if not self.is_connected:
            return
        try:
            pso = self._controller.runtime.commands.pso
            pso.psowindowconfigurefixedrange(axis, window_number, min_mm, max_mm)
            pso.psowindowoutputon(axis, window_number)
            if as_mask:
                pso.psoeventconfiguremask(axis, a1.PsoEventMask.WindowMask)
            else:
                pso.psooutputconfiguresource(axis, a1.PsoOutputSource.WindowOutput)
            print(f"[Aerotech] PSO ventana {window_number} -> eje {axis}, [{min_mm}, {max_mm}] mm, mask={as_mask}")
            self._pso_error = None
        except Exception as e:
            print(f"[Aerotech] Error en pso_configure_window({axis}): {e}")
            self._pso_error = f"PSO window failed ({axis}): {e}"

    def pso_configure_bitmap(self, axis=PSO_LASER_AXIS, bits: list = None):
        """Configura un patrón de bits (binary pattern) para disparo PSO.
        Sin uso real actualmente (Binary pattern se descartó del selector de
        Auto) — nombre corregido igualmente por consistencia, pero sin
        probar todavía contra hardware."""
        if not self.is_connected:
            return
        bits = bits or []
        try:
            self._controller.runtime.commands.pso.psobitmapconfigurearray(axis, list(bits))
            print(f"[Aerotech] PSO bitmap -> eje {axis}, {len(bits)} bits")
            self._pso_error = None
        except Exception as e:
            print(f"[Aerotech] Error en pso_configure_bitmap({axis}): {e}")
            self._pso_error = f"PSO bitmap failed ({axis}): {e}"

    def pso_output_on(self, axis=PSO_LASER_AXIS):
        """
        Activa la salida PSO directamente (sin pasar por Waveform/Distance) —
        es lo que usan el disparo de mantener-pulsado de Manual y el modo de
        alineación de Calibration.
        """
        if not self.is_connected:
            print("[Aerotech] Sin conexión — PSO output on ignorado")
            return
        try:
            self._controller.runtime.commands.pso.psooutputon(axis)
            print(f"[Aerotech] PSO output ON -> eje {axis}")
            self._pso_error = None
        except Exception as e:
            print(f"[Aerotech] Error en pso_output_on({axis}): {e}")
            self._pso_error = f"PSO output ON failed ({axis}): {e}"

    def pso_output_off(self, axis=PSO_LASER_AXIS):
        """Corta la salida PSO directamente — usado por el botón 'Laser stop'."""
        if not self.is_connected:
            return
        try:
            self._controller.runtime.commands.pso.psooutputoff(axis)
            print(f"[Aerotech] PSO output OFF -> eje {axis}")
            self._pso_error = None
        except Exception as e:
            print(f"[Aerotech] Error en pso_output_off({axis}): {e}")
            self._pso_error = f"PSO output OFF failed ({axis}): {e}"

    # ─────────────────────────────────────────────────────────────────
    # Secuencia de disparo — el relé debe estar cerrado antes de PSO
    # ─────────────────────────────────────────────────────────────────
    def fire_laser(self, power_percent: float):
        """
        Habilita el eje del láser, cierra el relé (si no lo estaba ya) y
        arma+dispara el PSO. Orden verificado en el laboratorio: sin el eje
        habilitado, DigitalOutputSet + PsoOutputOn no llegan a disparar.
        """
        self.enable_axes([PSO_LASER_AXIS])
        self.set_laser_board_power(True)
        self.pso_configure_waveform(power_percent=power_percent)
        self.pso_output_on()

    def stop_laser(self, cut_power: bool = False):
        """Corta el disparo PSO. Si cut_power=True, también abre el relé."""
        self.pso_output_off()
        if cut_power:
            self.set_laser_board_power(False)
