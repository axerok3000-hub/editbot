from html import escape

from .fonts import to_gothic, to_italic_unicode

DEFAULT_STYLE = "normal"

# key -> label shown on the /style menu buttons
STYLES: dict[str, str] = {
    "normal": "Обычный",
    "bold": "Жирный",
    "italic": "Курсив",
    "strike": "Зачёркнутый",
    "mono": "Моноширинный",
    "gothic": "Готический",
    "italic_unicode": "Курсивный юникод",
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
    if style == "gothic":
        return to_gothic(text), None
    if style == "italic_unicode":
        return to_italic_unicode(text), None
    return text, None
