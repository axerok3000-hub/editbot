from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from ..config import Config
from ..db import SettingsStore
from ..styles import STYLES
from .filters import IsOwner

router = Router(name="style")

router.message.filter(IsOwner())
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
    rows.append([InlineKeyboardButton(text="Закрыть", callback_data="style:close")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(Command("style"))
async def cmd_style(message: Message, settings: SettingsStore, config: Config) -> None:
    current = settings.get_style(config.owner_id)
    await message.answer(
        "Выбери стиль для исходящих сообщений:", reply_markup=_style_keyboard(current)
    )


@router.callback_query(F.data.startswith("style:"))
async def cb_style(callback: CallbackQuery, settings: SettingsStore, config: Config) -> None:
    key = callback.data.split(":", 1)[1]

    if key == "close":
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            await callback.message.edit_text("Меню стилей закрыто.")
        await callback.answer()
        return

    if key not in STYLES:
        await callback.answer()
        return

    settings.set_style(config.owner_id, key)
    await callback.message.edit_reply_markup(reply_markup=_style_keyboard(key))
    await callback.answer(f"Стиль: {STYLES[key]}")
