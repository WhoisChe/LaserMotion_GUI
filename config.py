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


import json
import os

from PySide6.QtCore import QSettings

# Mismas funciones que usa Custom_Widgets.Qss.colorsystem.CreateColorVariable
# para derivar BG_2/BG_3/CT_2/CA_2/CA_3 a partir de los tres colores base de
# cada tema y volcarlos a Qss/scss/_variables.scss — se reutilizan aquí (no
# se reimplementan) para que config.THEME quede en sincronía exacta con el
# QSS ya compilado.
from Custom_Widgets.Qss.colorsystem import (
    adjust_lightness,
    darken_color,
    is_color_dark_or_light,
    lighten_color,
)

_STYLE_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "json-styles", "style.json")

# Última red de seguridad si json-styles/style.json no se puede leer en
# absoluto (fichero borrado/corrupto) — gris neutro, NO los colores de
# ningún tema concreto (ese hardcodeo de una paleta fija fue la causa
# original de que THEME se quedara pegado a TIDE).
_EMERGENCY_FALLBACK_COLORS = {
    "COLOR_BACKGROUND_1": "#FFFFFF",
    "COLOR_BACKGROUND_2": "#F0F0F0",
    "COLOR_BACKGROUND_3": "#E0E0E0",
    "COLOR_TEXT_1": "#000000",
    "COLOR_TEXT_2": "#333333",
    "COLOR_ACCENT_1": "#808080",
    "COLOR_ACCENT_2": "#666666",
    "COLOR_ACCENT_3": "#4D4D4D",
}


def _load_style_themes():
    """Lee json-styles/style.json y devuelve (org_name, app_name,
    {Theme-name: bloque}, bloque_por_defecto). Mismo patrón de resolución de
    organización/aplicación que _current_icons_color() en
    src/ui_interface.py — necesario porque QCoreApplication puede no tener
    todavía el organization/application name fijado por Custom_Widgets
    cuando esto se llama."""
    org_name = ""
    app_name = ""
    themes = {}
    default_theme = None

    try:
        with open(_STYLE_JSON_PATH, encoding="utf-8") as f:
            style = json.load(f)
        for qsettings_block in style.get("QSettings", []):
            app_settings = qsettings_block.get("AppSettings", {})
            org_name = str(app_settings.get("OrginizationName", ""))
            app_name = str(app_settings.get("ApplicationName", ""))
            for theme_settings in qsettings_block.get("ThemeSettings", []):
                for theme in theme_settings.get("CustomTheme", []):
                    name = theme.get("Theme-name")
                    if not name:
                        continue
                    themes[name] = theme
                    if theme.get("Default-Theme"):
                        default_theme = theme
    except Exception:
        pass

    return org_name, app_name, themes, default_theme


def _active_theme_palette():
    """Bloque de tema (Background-color/Text-color/Accent-color) activo
    ahora mismo, según el valor guardado en QSettings por
    GuiFunctions.changeAppTheme() (main.py). Si no hay tema guardado (primer
    arranque) o no se reconoce, recae en Default-Theme del propio JSON."""
    org_name, app_name, themes, default_theme = _load_style_themes()
    if not themes:
        return None

    settings = QSettings(org_name, app_name) if org_name and app_name else QSettings()
    active_name = settings.value("THEME")
    if not active_name:
        return default_theme
    return themes.get(str(active_name), default_theme)


def _derive_theme_colors(palette):
    """Reproduce el algoritmo de sombras de
    Custom_Widgets.Qss.colorsystem.CreateColorVariable (BG_2/BG_3 a partir
    de Background-color, CT_2/CA_2/CA_3 a partir de Text-color/Accent-color)
    para los tres colores base de un tema del JSON."""
    bg = palette["Background-color"]
    text = palette["Text-color"]
    accent = palette["Accent-color"]

    if is_color_dark_or_light(bg) == "light":
        bg_2 = darken_color(bg, 0.05)
        bg_3 = darken_color(bg, 0.1)
    else:
        bg_2 = adjust_lightness(bg, 0.90)
        bg_3 = adjust_lightness(bg, 0.80)

    # NOTA: al igual que en Custom_Widgets.Qss.colorsystem, tanto el matiz de
    # texto como los de acento se deciden mirando si el TEXTO (no el acento)
    # es claro u oscuro — se replica tal cual para que el resultado coincida
    # exactamente con el QSS ya compilado por Custom_Widgets.
    if is_color_dark_or_light(text) == "light":
        text_2 = darken_color(text, 0.2)
        accent_2 = darken_color(accent, 0.2)
        accent_3 = darken_color(accent, 0.4)
    else:
        text_2 = lighten_color(text, 0.2)
        accent_2 = lighten_color(accent, 0.2)
        accent_3 = lighten_color(accent, 0.4)

    return {
        "COLOR_BACKGROUND_1": bg,
        "COLOR_BACKGROUND_2": bg_2,
        "COLOR_BACKGROUND_3": bg_3,
        "COLOR_TEXT_1": text,
        "COLOR_TEXT_2": text_2,
        "COLOR_ACCENT_1": accent,
        "COLOR_ACCENT_2": accent_2,
        "COLOR_ACCENT_3": accent_3,
    }


class _ThemeMeta(type):
    """Resuelve THEME.COLOR_* leyendo el tema activo en cada acceso, en vez
    de fijarlo una vez a los valores de un tema concreto. Así el código
    Python que lee config.THEME.COLOR_* directamente (GlobalStatusPanel,
    LEDs, ui_extensions_*.py) sigue al tema elegido en `themeList` igual que
    ya hacía el QSS compilado por Custom_Widgets."""

    def __getattr__(cls, name):
        if name not in _EMERGENCY_FALLBACK_COLORS:
            raise AttributeError(name)
        palette = _active_theme_palette()
        if palette is None:
            return _EMERGENCY_FALLBACK_COLORS[name]
        try:
            return _derive_theme_colors(palette)[name]
        except Exception:
            return _EMERGENCY_FALLBACK_COLORS[name]


class THEME(metaclass=_ThemeMeta):
    """Paleta de colores de la interfaz — resuelta dinámicamente contra el
    tema activo (QSettings + json-styles/style.json), no fijada a un tema
    concreto. Ver _ThemeMeta y _active_theme_palette()."""
