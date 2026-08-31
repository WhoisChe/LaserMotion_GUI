########################################################################
## UTILIDAD DE CONTRASTE (WCAG) — ver 19_verificacion_contraste.md
## Luminancia relativa y ratio de contraste estándar (fórmula WCAG 2.x),
## reutilizada por audit_contrast.py para comprobar cada pareja
## texto/fondo conocida del proyecto contra los 3 temas.
########################################################################

# Umbral estándar WCAG AA para texto normal (no en negrita grande) — por
# debajo de esto, el texto es difícil de leer.
WCAG_AA_NORMAL_TEXT_MIN_RATIO = 4.5


def relative_luminance(hex_color: str) -> float:
    """Luminancia relativa de un color (0.0 = negro, 1.0 = blanco)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def linearize(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = linearize(r), linearize(g), linearize(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(color_a: str, color_b: str) -> float:
    """Ratio de contraste WCAG entre dos colores — de 1:1 (idéntico) a 21:1
    (negro sobre blanco). >= 4.5 es el mínimo AA para texto normal."""
    l1, l2 = relative_luminance(color_a), relative_luminance(color_b)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def readable_text_color(bg_hex: str, light: str = "#FFFFFF", dark: str = "#06112B") -> str:
    """Elige `light` u `dark` — lo que dé más contraste contra bg_hex.
    Para texto fijo emparejado con un fondo de tema (THEME.COLOR_ACCENT_1/2,
    que cambia de claro a oscuro según el tema activo — ni blanco ni oscuro
    fijo sirve en los 3 a la vez), ver 19_verificacion_contraste.md."""
    if contrast_ratio(light, bg_hex) >= contrast_ratio(dark, bg_hex):
        return light
    return dark
