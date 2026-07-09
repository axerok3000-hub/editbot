"""Unicode character substitution tables for fancy latin-only text styles.

Cyrillic and everything else is left untouched — only ASCII a-z/A-Z are mapped.
"""

# Mathematical Fraktur (U+1D504-1D537), with the canonical exceptions for
# C, H, I, R, Z which reuse the older Letterlike Symbols block.
GOTHIC_MAP: dict[str, str] = {
    "A": "\U0001D504", "B": "\U0001D505", "C": "\U0000212D", "D": "\U0001D507",
    "E": "\U0001D508", "F": "\U0001D509", "G": "\U0001D50A", "H": "\U0000210C",
    "I": "\U00002111", "J": "\U0001D50D", "K": "\U0001D50E", "L": "\U0001D50F",
    "M": "\U0001D510", "N": "\U0001D511", "O": "\U0001D512", "P": "\U0001D513",
    "Q": "\U0001D514", "R": "\U0000211C", "S": "\U0001D516", "T": "\U0001D517",
    "U": "\U0001D518", "V": "\U0001D519", "W": "\U0001D51A", "X": "\U0001D51B",
    "Y": "\U0001D51C", "Z": "\U00002128",
    "a": "\U0001D51E", "b": "\U0001D51F", "c": "\U0001D520", "d": "\U0001D521",
    "e": "\U0001D522", "f": "\U0001D523", "g": "\U0001D524", "h": "\U0001D525",
    "i": "\U0001D526", "j": "\U0001D527", "k": "\U0001D528", "l": "\U0001D529",
    "m": "\U0001D52A", "n": "\U0001D52B", "o": "\U0001D52C", "p": "\U0001D52D",
    "q": "\U0001D52E", "r": "\U0001D52F", "s": "\U0001D530", "t": "\U0001D531",
    "u": "\U0001D532", "v": "\U0001D533", "w": "\U0001D534", "x": "\U0001D535",
    "y": "\U0001D536", "z": "\U0001D537",
}

# Mathematical Italic (U+1D434-1D467), with the canonical exception for
# lowercase h which reuses the Planck constant symbol.
ITALIC_UNICODE_MAP: dict[str, str] = {
    "A": "\U0001D434", "B": "\U0001D435", "C": "\U0001D436", "D": "\U0001D437",
    "E": "\U0001D438", "F": "\U0001D439", "G": "\U0001D43A", "H": "\U0001D43B",
    "I": "\U0001D43C", "J": "\U0001D43D", "K": "\U0001D43E", "L": "\U0001D43F",
    "M": "\U0001D440", "N": "\U0001D441", "O": "\U0001D442", "P": "\U0001D443",
    "Q": "\U0001D444", "R": "\U0001D445", "S": "\U0001D446", "T": "\U0001D447",
    "U": "\U0001D448", "V": "\U0001D449", "W": "\U0001D44A", "X": "\U0001D44B",
    "Y": "\U0001D44C", "Z": "\U0001D44D",
    "a": "\U0001D44E", "b": "\U0001D44F", "c": "\U0001D450", "d": "\U0001D451",
    "e": "\U0001D452", "f": "\U0001D453", "g": "\U0001D454", "h": "\U0000210E",
    "i": "\U0001D456", "j": "\U0001D457", "k": "\U0001D458", "l": "\U0001D459",
    "m": "\U0001D45A", "n": "\U0001D45B", "o": "\U0001D45C", "p": "\U0001D45D",
    "q": "\U0001D45E", "r": "\U0001D45F", "s": "\U0001D460", "t": "\U0001D461",
    "u": "\U0001D462", "v": "\U0001D463", "w": "\U0001D464", "x": "\U0001D465",
    "y": "\U0001D466", "z": "\U0001D467",
}


def _apply_map(text: str, mapping: dict[str, str]) -> str:
    return "".join(mapping.get(ch, ch) for ch in text)


def to_gothic(text: str) -> str:
    return _apply_map(text, GOTHIC_MAP)


def to_italic_unicode(text: str) -> str:
    return _apply_map(text, ITALIC_UNICODE_MAP)
