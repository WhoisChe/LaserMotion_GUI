########################################################################
## AUDITORÍA DE CONTRASTE TEXTO/FONDO — LOS 3 TEMAS
## ver 19_verificacion_contraste.md
##
## Recorre cada pareja conocida de color de texto/fondo fijada
## explícitamente en el proyecto (main.py, src/ui_extensions_*.py,
## src/ui_interface.py) y comprueba su contraste WCAG contra TIDE, NEON y
## EMBER, usando config.THEME ya corregido para leer el tema activo
## dinámicamente (ver config.py).
##
## Uso: python audit_contrast.py
## Código de salida: 0 si todas las parejas superan 4.5:1 en los 3 temas,
## 1 si alguna combinación queda por debajo.
########################################################################

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from PySide6.QtCore import QSettings

import config
from src.color_contrast import WCAG_AA_NORMAL_TEXT_MIN_RATIO, contrast_ratio, readable_text_color

THEMES = ("TIDE", "NEON", "EMBER")


def _resolve(value):
    """'THEME.COLOR_TEXT_1' -> config.THEME.COLOR_TEXT_1 (leído en el
    momento de la llamada, con el tema activo ya fijado en QSettings).
    'READABLE:THEME.COLOR_ACCENT_2' -> readable_text_color(config.THEME.COLOR_ACCENT_2)
    (mismo cálculo que hacen en caliente los estados :hover que usan
    readable_text_color() en vez de un "white" fijo). Un valor que ya es un
    hex literal ('#RRGGBB') se devuelve tal cual."""
    if isinstance(value, str) and value.startswith("READABLE:THEME."):
        bg = getattr(config.THEME, value.split(".", 1)[1])
        return readable_text_color(bg)
    if isinstance(value, str) and value.startswith("THEME."):
        return getattr(config.THEME, value.split(".", 1)[1])
    return value


# Cada entrada es una pareja texto/fondo tal como aparece realmente en el
# código (main.py, src/ui_extensions_*.py, src/ui_interface.py) — el
# fondo es el que el widget pinta de verdad (si el widget es transparente,
# se usa el fondo efectivo del contenedor: la página, que por la QSS
# global de Custom_Widgets siempre acaba resolviéndose a
# THEME.COLOR_BACKGROUND_1 — ver generated-files/css/main.css, regla
# "QWidget { background-color: ... }" + "#mainPagesCont ... QFrame {
# background-color: transparent; }").
CHECKS = [
    # ── main.py — GlobalStatusPanel ─────────────────────────────────────
    ("GlobalStatusPanel: connection label", "THEME.COLOR_TEXT_1", "THEME.COLOR_BACKGROUND_1"),
    ("GlobalStatusPanel: axis label / position value", "THEME.COLOR_TEXT_1", "THEME.COLOR_BACKGROUND_1"),
    ("GlobalStatusPanel: indicator text (Enabled/Homed/CW-CCW)", "THEME.COLOR_TEXT_1", "THEME.COLOR_BACKGROUND_1"),
    ("GlobalStatusPanel: Laser stop button", "#FFFFFF", "#D32F2F"),

    # ── src/ui_extensions_gcode.py — drag & drop ─────────────────────────
    # dragYdrop ya no se queda en el gris fijo de Designer (rgb(175,175,175))
    # — setup_drag_drop_area() aplica el mismo estilo "en reposo" de tema
    # que drop_event() (_apply_default_drop_style()), así que el fondo es
    # siempre BACKGROUND_3 salvo mientras se arrastra un archivo encima.
    ("G-Code drag&drop: label (reposo / tras soltar archivo)", "THEME.COLOR_TEXT_2", "THEME.COLOR_BACKGROUND_3"),
    ("G-Code drag&drop: label (arrastrando encima, chip propio)", "#06112B", "#FFFFFF"),
    ("G-Code drag&drop: mensaje 'archivo cargado' (chip propio)", "#FFFFFF", "#2E7D32"),
    ("G-Code drag&drop: mensaje de error (chip propio)", "#FFFFFF", "#B71C1C"),
    ("G-Code drag&drop: botón eliminar archivo (✕)", "#FFFFFF", "#D32F2F"),

    # ── src/ui_extensions_gcode.py — resto de la página ─────────────────
    ("G-Code: título de página", "THEME.COLOR_TEXT_1", "THEME.COLOR_BACKGROUND_1"),
    ("G-Code: vista previa (gcodePreview)", "#F0F0F0", "#2B2B2B"),
    # GCodeEditorDialog mantiene un fondo claro fijo (#F5F5F5) igual que su
    # editor de texto interno — su texto también es fijo, no de tema (ver
    # comentario junto a title_label en ui_extensions_gcode.py).
    ("G-Code editor: título (titleLabel)", "#06112B", "#F5F5F5"),
    ("G-Code editor: info de archivo (infoLabel)", "#015185", "#F5F5F5"),
    ("G-Code editor: ayuda (helpLabel)", "#015185", "#F5F5F5"),
    ("G-Code editor: editor de texto", "#F0F0F0", "#2B2B2B"),

    # ── src/ui_extensions_auto.py ────────────────────────────────────────
    ("Auto: título de sección/labels de panel", "THEME.COLOR_TEXT_1", "THEME.COLOR_BACKGROUND_1"),
    ("Auto: vista previa (gcodePreviewAuto)", "#F0F0F0", "#2B2B2B"),
    ("Auto/Manual: botón eje — reposo", "THEME.COLOR_TEXT_1", "THEME.COLOR_BACKGROUND_2"),
    ("Auto/Manual: botón eje — hover (Enable)", "READABLE:THEME.COLOR_ACCENT_2", "THEME.COLOR_ACCENT_2"),
    ("Auto/Manual: botón Home — hover", "READABLE:THEME.COLOR_ACCENT_1", "THEME.COLOR_ACCENT_1"),
    ("Auto/Manual: botón eje — checked (enabled)", "#FFFFFF", "#2E7D32"),

    # ── src/ui_extensions_manual.py ──────────────────────────────────────
    ("Manual: DARK_FIELD_STYLE — reposo / hover (:hover ya no fija color)", "#EAE8E2", "#06112B"),
    ("Manual: DARK_FIELD_STYLE — focus", "#06112B", "#EAE8E2"),
    ("Manual: DARK_COMBO_STYLE — reposo", "#EAE8E2", "#06112B"),
    ("Manual: DARK_CONFIRM_BTN_STYLE — reposo", "#EAE8E2", "#06112B"),
    ("Manual: DARK_CONFIRM_BTN_STYLE — hover/pressed", "#EAE8E2", "#015185"),
    ("Manual: label de eje / título Movimiento XYZ", "THEME.COLOR_TEXT_1", "THEME.COLOR_BACKGROUND_1"),
    ("Manual: labelLaserPowerManual (consigna)", "THEME.COLOR_TEXT_1", "THEME.COLOR_BACKGROUND_1"),
    ("Manual: laserFireBtn", "#FFFFFF", "#D32F2F"),
    ("Manual: laserBoardPowerBtn — hover", "READABLE:THEME.COLOR_ACCENT_2", "THEME.COLOR_ACCENT_2"),

    # ── src/ui_extensions_home.py ────────────────────────────────────────
    ("Home: laserTitleLabel / labelLaserState", "THEME.COLOR_TEXT_1", "THEME.COLOR_BACKGROUND_1"),

    # ── src/ui_extensions_connection.py ──────────────────────────────────
    ("Connection: títulos / labels", "THEME.COLOR_TEXT_1", "THEME.COLOR_BACKGROUND_1"),
    ("Connection: hostAddressInput / connectBtn — reposo", "THEME.COLOR_TEXT_1", "THEME.COLOR_BACKGROUND_2"),
    ("Connection: connectBtn — hover", "READABLE:THEME.COLOR_ACCENT_2", "THEME.COLOR_ACCENT_2"),
    ("Connection: connectBtn — checked (conectado)", "#FFFFFF", "#2E7D32"),

    # Master safety window (src/ui_extensions_manual.py, migrada desde la
    # antigua página Calibration): mismos pares de color ya cubiertos arriba
    # (THEME.COLOR_TEXT_1/BACKGROUND_2 para los campos xMin/xMax/yMin/yMax,
    # #FFFFFF/#2E7D32 para los botones Corner 1/2 — ver líneas 95 y 114).
]


def run_audit():
    settings = QSettings("Laser UI", "Laser UI Company")
    original_theme = settings.value("THEME")

    failures = []
    total_combinations = 0
    try:
        for theme_name in THEMES:
            settings.setValue("THEME", theme_name)
            for entry in CHECKS:
                label, text_src, bg_src = entry[0], entry[1], entry[2]
                applicable_themes = entry[3] if len(entry) > 3 else THEMES
                if theme_name not in applicable_themes:
                    continue
                total_combinations += 1
                text_color = _resolve(text_src)
                bg_color = _resolve(bg_src)
                ratio = contrast_ratio(text_color, bg_color)
                if ratio < WCAG_AA_NORMAL_TEXT_MIN_RATIO:
                    failures.append((theme_name, label, text_color, bg_color, ratio))
    finally:
        if original_theme:
            settings.setValue("THEME", original_theme)

    print(f"Comprobadas {len(CHECKS)} parejas texto/fondo x {len(THEMES)} temas "
          f"= {total_combinations} combinaciones aplicables.\n")

    if not failures:
        print(f"OK — ninguna combinación por debajo de {WCAG_AA_NORMAL_TEXT_MIN_RATIO}:1.")
        return 0

    print(f"FALLOS — {len(failures)} combinación(es) por debajo de "
          f"{WCAG_AA_NORMAL_TEXT_MIN_RATIO}:1:\n")
    for theme_name, label, text_color, bg_color, ratio in failures:
        print(f"  [{theme_name}] {label}: texto {text_color} sobre fondo {bg_color} "
              f"-> {ratio:.2f}:1")
    return 1


if __name__ == "__main__":
    sys.exit(run_audit())
