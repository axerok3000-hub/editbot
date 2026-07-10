import math

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from ..config import Config
from ..db import SettingsStore
from ..styles import STYLES
from .filters import IsOwner

router = Router(name="style")

router.callback_query.filter(IsOwner())

STYLE_KEYS = list(STYLES.keys())
PAGE_SIZE = 6
PAGE_COUNT = math.ceil(len(STYLE_KEYS) / PAGE_SIZE)


def _page_for_style(style: str) -> int:
    try:
        index = STYLE_KEYS.index(style)
    except ValueError:
        index = 0
    return index // PAGE_SIZE


def _style_keyboard(current: str, page: int) -> InlineKeyboardMarkup:
    page = max(0, min(page, PAGE_COUNT - 1))
    page_keys = STYLE_KEYS[page * PAGE_SIZE : page * PAGE_SIZE + PAGE_SIZE]

    rows = []
    for i in range(0, len(page_keys), 2):
        row = []
        for key in page_keys[i : i + 2]:
            marker = "🔵" if key == current else "🔴"
            row.append(
                InlineKeyboardButton(text=f"{marker} {STYLES[key]}", callback_data=f"style:{key}")
            )
        rows.append(row)

    prev_page = page - 1 if page > 0 else None
    next_page = page + 1 if page < PAGE_COUNT - 1 else None
    rows.append(
        [
            InlineKeyboardButton(
                text="◀️", callback_data=f"stylepage:{prev_page}" if prev_page is not None else "stylepage:noop"
            ),
            InlineKeyboardButton(text=f"{page + 1}/{PAGE_COUNT}", callback_data="stylepage:noop"),
            InlineKeyboardButton(
                text="▶️", callback_data=f"stylepage:{next_page}" if next_page is not None else "stylepage:noop"
            ),
        ]
    )
    rows.append([InlineKeyboardButton(text="◀️ Назад", callback_data="menu:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "menu:style")
async def cb_style_menu(callback: CallbackQuery, settings: SettingsStore, config: Config) -> None:
    current = settings.get_style(config.owner_id)
    text = "🎨 Стиль\n\nВыбери стиль для исходящих сообщений:"
    await callback.message.edit_text(text, reply_markup=_style_keyboard(current, _page_for_style(current)))
    await callback.answer()


@router.callback_query(F.data.startswith("stylepage:"))
async def cb_style_page(callback: CallbackQuery, settings: SettingsStore, config: Config) -> None:
    raw = callback.data.split(":", 1)[1]
    if raw == "noop":
        await callback.answer()
        return
    current = settings.get_style(config.owner_id)
    await callback.message.edit_reply_markup(reply_markup=_style_keyboard(current, int(raw)))
    await callback.answer()


@router.callback_query(F.data.startswith("style:"))
async def cb_style_select(callback: CallbackQuery, settings: SettingsStore, config: Config) -> None:
    key = callback.data.split(":", 1)[1]
    if key not in STYLES:
        await callback.answer()
        return

    settings.set_style(config.owner_id, key)
    await callback.message.edit_reply_markup(reply_markup=_style_keyboard(key, _page_for_style(key)))
    await callback.answer(f"Стиль: {STYLES[key]}")
