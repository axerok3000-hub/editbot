"""Unicode character substitution tables for fancy text styles.

Unicode has no dedicated "gothic"/"small-caps"/etc. glyphs for Cyrillic
(unlike Latin, which got its own Mathematical Alphanumeric Symbols block
and friends) - such letterforms simply don't exist as separate codepoints.
As a partial approximation, the handful of Cyrillic letters that are
near-identical in shape to a Latin letter (the same set used as IDN
homograph confusables) are mapped through their Latin lookalike before
styling. Everything else - digits, punctuation, spaces, and the ~20
Cyrillic letters with no Latin lookalike - is left untouched, never raises.
"""

# Cyrillic letters that are visually near-identical to a Latin letter.
CYRILLIC_TO_LATIN_HOMOGLYPHS: dict[str, str] = {
    "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H",
    "О": "O", "Р": "P", "С": "C", "Т": "T", "У": "Y", "Х": "X",
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x",
}

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

# Elder Futhark-ish runes. Case-insensitive (runes have no case); c, q, v, x
# have no given rune and are left untouched.
RUNES_MAP: dict[str, str] = {
    "a": "ᚨ", "b": "ᛒ", "d": "ᛞ", "e": "ᛖ", "f": "ᚠ", "g": "ᚷ", "h": "ᚺ",
    "i": "ᛁ", "j": "ᛃ", "k": "ᚲ", "l": "ᛚ", "m": "ᛗ", "n": "ᚾ", "o": "ᛟ",
    "p": "ᛈ", "r": "ᚱ", "s": "ᛊ", "t": "ᛏ", "u": "ᚢ", "w": "ᚹ", "y": "ᛇ", "z": "ᛉ",
}
RUNES_MAP.update({k.upper(): v for k, v in list(RUNES_MAP.items())})

# Enclosed Alphanumerics (U+24B6-24CF upper, U+24D0-24E9 lower) - "bubbles".
BUBBLES_MAP: dict[str, str] = {
    **{chr(65 + i): chr(0x24B6 + i) for i in range(26)},
    **{chr(97 + i): chr(0x24D0 + i) for i in range(26)},
}

# Enclosed Alphanumeric Supplement (U+1F130-1F149) - squared capitals only,
# Unicode has no squared lowercase, so lowercase input is upper-cased first.
SQUARES_MAP: dict[str, str] = {chr(65 + i): chr(0x1F130 + i) for i in range(26)}
SQUARES_MAP.update({chr(97 + i): chr(0x1F130 + i) for i in range(26)})

# Latin Letter Small Capitals, scattered across IPA Extensions / Phonetic
# Extensions. Only lowercase is mapped (that's what "small caps" styles -
# regular capitals stay as regular capitals, same as real typography).
# No small-capital exists for "s" and "x"; left as-is.
SMALL_CAPS_MAP: dict[str, str] = {
    "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ꜰ", "g": "ɢ",
    "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ",
    "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ", "s": "ꜱ", "t": "ᴛ", "u": "ᴜ",
    "v": "ᴠ", "w": "ᴡ", "y": "ʏ", "z": "ᴢ",
}

# Mathematical Double-Struck (U+1D538-1D56B), with the canonical exceptions
# for C, H, N, P, Q, R, Z which reuse the "number set" Letterlike Symbols.
DOUBLE_STRUCK_MAP: dict[str, str] = {
    "A": "\U0001D538", "B": "\U0001D539", "C": "\U00002102", "D": "\U0001D53B",
    "E": "\U0001D53C", "F": "\U0001D53D", "G": "\U0001D53E", "H": "\U0000210D",
    "I": "\U0001D540", "J": "\U0001D541", "K": "\U0001D542", "L": "\U0001D543",
    "M": "\U0001D544", "N": "\U00002115", "O": "\U0001D546", "P": "\U00002119",
    "Q": "\U0000211A", "R": "\U0000211D", "S": "\U0001D54A", "T": "\U0001D54B",
    "U": "\U0001D54C", "V": "\U0001D54D", "W": "\U0001D54E", "X": "\U0001D54F",
    "Y": "\U0001D550", "Z": "\U00002124",
    "a": "\U0001D552", "b": "\U0001D553", "c": "\U0001D554", "d": "\U0001D555",
    "e": "\U0001D556", "f": "\U0001D557", "g": "\U0001D558", "h": "\U0001D559",
    "i": "\U0001D55A", "j": "\U0001D55B", "k": "\U0001D55C", "l": "\U0001D55D",
    "m": "\U0001D55E", "n": "\U0001D55F", "o": "\U0001D560", "p": "\U0001D561",
    "q": "\U0001D562", "r": "\U0001D563", "s": "\U0001D564", "t": "\U0001D565",
    "u": "\U0001D566", "v": "\U0001D567", "w": "\U0001D568", "x": "\U0001D569",
    "y": "\U0001D56A", "z": "\U0001D56B",
}

# Upside-down lookalikes. Only lowercase is mapped - uppercase input is
# rendered with the same rotated glyph (Unicode has no reliable full set of
# rotated capitals), which is what most "flip text" generators do too.
UPSIDE_DOWN_MAP: dict[str, str] = {
    "a": "ɐ", "b": "q", "c": "ɔ", "d": "p", "e": "ǝ", "f": "ɟ", "g": "ƃ",
    "h": "ɥ", "i": "ᴉ", "j": "ɾ", "k": "ʞ", "l": "l", "m": "ɯ", "n": "u",
    "o": "o", "p": "d", "q": "b", "r": "ɹ", "s": "s", "t": "ʇ", "u": "n",
    "v": "ʌ", "w": "ʍ", "x": "x", "y": "ʎ", "z": "z",
}


def _apply_map(text: str, mapping: dict[str, str]) -> str:
    result = []
    for ch in text:
        if ch in mapping:
            result.append(mapping[ch])
            continue
        latin = CYRILLIC_TO_LATIN_HOMOGLYPHS.get(ch)
        result.append(mapping.get(latin, latin) if latin is not None else ch)
    return "".join(result)


def to_gothic(text: str) -> str:
    return _apply_map(text, GOTHIC_MAP)


def to_italic_unicode(text: str) -> str:
    return _apply_map(text, ITALIC_UNICODE_MAP)


def to_runes(text: str) -> str:
    return _apply_map(text, RUNES_MAP)


def to_bubbles(text: str) -> str:
    return _apply_map(text, BUBBLES_MAP)


def to_squares(text: str) -> str:
    return _apply_map(text, SQUARES_MAP)


def to_small_caps(text: str) -> str:
    return _apply_map(text, SMALL_CAPS_MAP)


def to_double_struck(text: str) -> str:
    return _apply_map(text, DOUBLE_STRUCK_MAP)


def to_upside_down(text: str) -> str:
    flipped = []
    for ch in text:
        lower = ch.lower()
        if lower in UPSIDE_DOWN_MAP:
            flipped.append(UPSIDE_DOWN_MAP[lower])
            continue
        latin = CYRILLIC_TO_LATIN_HOMOGLYPHS.get(ch)
        flipped.append(UPSIDE_DOWN_MAP.get(latin.lower(), latin) if latin is not None else ch)
    return "".join(reversed(flipped))


# style key -> transform function, used by /style for the substitution-based
# fonts (bold/italic/strike/mono are plain HTML tags, handled in styles.py).
FONTS: dict[str, "callable"] = {
    "gothic": to_gothic,
    "italic_unicode": to_italic_unicode,
    "runes": to_runes,
    "bubbles": to_bubbles,
    "squares": to_squares,
    "upside_down": to_upside_down,
    "small_caps": to_small_caps,
    "double_struck": to_double_struck,
}


def apply_font(text: str, style: str) -> str:
    fn = FONTS.get(style)
    return fn(text) if fn else text
