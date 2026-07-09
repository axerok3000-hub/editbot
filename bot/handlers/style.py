from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from ..config import Config
from ..db import SettingsStore
from ..styles import STYLES
from .filters import IsOwner

router = Router(name="style")

router.callback_query.filter(IsOwner())

_LAYOUT = [
    ["normal"],
    ["bold", "italic"],
    ["strike", "mono"],
    ["gothic", "italic_unicode"],
]


def _style_keyboard(current: str) -> InlineKeyboardMarkup:
    rows = []
    for row_keys in _LAYOUT:
        row = []
        for key in row_keys:
            marker = "🔵" if key == current else "🔴"
            row.append(
                InlineKeyboardButton(text=f"{marker} {STYLES[key]}", callback_data=f"style:{key}")
            )
        rows.append(row)
    rows.append([InlineKeyboardButton(text="◀️ Назад", callback_data="menu:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "menu:style")
async def cb_style_menu(callback: CallbackQuery, settings: SettingsStore, config: Config) -> None:
    current = settings.get_style(config.owner_id)
    text = "🎨 Стиль\n\nВыбери стиль для исходящих сообщений:"
    await callback.message.edit_text(text, reply_markup=_style_keyboard(current))
    await callback.answer()


@router.callback_query(F.data.startswith("style:"))
async def cb_style_select(callback: CallbackQuery, settings: SettingsStore, config: Config) -> None:
    key = callback.data.split(":", 1)[1]
    if key not in STYLES:
        await callback.answer()
        return

    settings.set_style(config.owner_id, key)
    await callback.message.edit_reply_markup(reply_markup=_style_keyboard(key))
    await callback.answer(f"Стиль: {STYLES[key]}")
