from html import escape

from .fonts import FONTS, apply_font

DEFAULT_STYLE = "normal"

# key -> label shown on the /style menu buttons. Order matters: it drives
# pagination (see bot/handlers/style.py).
STYLES: dict[str, str] = {
    "normal": "Обычный",
    "bold": "Жирный",
    "italic": "Курсив",
    "strike": "Зачёркнутый",
    "mono": "Моноширинный",
    "gothic": "Готический",
    "italic_unicode": "Курсивный юникод",
    "runes": "Руны",
    "bubbles": "Пузырьки",
    "squares": "Квадраты",
    "upside_down": "Наоборот",
    "small_caps": "Мелкий",
    "double_struck": "Двойной",
}


def apply_style(text: str, style: str) -> tuple[str, str | None]:
    """Returns (rendered_text, parse_mode) for the given style."""
    if style == "bold":
        return f"<b>{escape(text)}</b>", "HTML"
    if style == "italic":
        return f"<i>{escape(text)}</i>", "HTML"
    if style == "strike":
        return f"<s>{escape(text)}</s>", "HTML"
    if style == "mono":
        return f"<code>{escape(text)}</code>", "HTML"
    if style in FONTS:
        return apply_font(text, style), None
    return text, None
