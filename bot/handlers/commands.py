from datetime import datetime, timezone
from html import escape

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from ..config import Config
from ..db import KnownChatsStore, MessageCache
from ..storage import ConnectionStore, ExcludedChatsStore
from .filters import IsOwner

router = Router(name="commands")

router.message.filter(IsOwner())
router.callback_query.filter(IsOwner())

MAX_EXCLUSION_CHATS_SHOWN = 15


def _format_date(timestamp: int | None) -> str:
    if timestamp is None:
        return "—"
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _main_menu_text(store: ConnectionStore, config: Config) -> str:
    connection = store.get_for_owner(config.owner_id)
    connected = connection is not None and connection.is_enabled
    return (
        "🤖 EditBot\n\n"
        f"Соединение: {'✅ подключено' if connected else '❌ нет'}\n"
        "Эффектов: 5"
    )


def _main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 Профиль", callback_data="menu:profile"),
                InlineKeyboardButton(text="🔗 Соединение", callback_data="menu:conn"),
            ],
            [
                InlineKeyboardButton(text="🎨 Стиль", callback_data="menu:style"),
                InlineKeyboardButton(text="🚫 Исключения", callback_data="menu:exclusions"),
            ],
            [InlineKeyboardButton(text="🗑 Мои удалённые", callback_data="menu:deleted")],
            [
                InlineKeyboardButton(text="✨ Эффекты", callback_data="menu:effects"),
                InlineKeyboardButton(text="🎮 Игры", callback_data="menu:games"),
            ],
        ]
    )


def _back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="menu:back")]]
    )


@router.message(CommandStart())
async def cmd_start(message: Message, store: ConnectionStore, config: Config) -> None:
    await message.answer(_main_menu_text(store, config), reply_markup=_main_menu_keyboard())


@router.callback_query(F.data == "menu:profile")
async def cb_profile(callback: CallbackQuery, store: ConnectionStore, config: Config) -> None:
    connection = store.get_for_owner(config.owner_id)
    connected_at = connection.connected_at if connection else None
    text = (
        "👤 Профиль\n\n"
        f"user_id: {config.owner_id}\n"
        f"Дата подключения: {_format_date(connected_at)}"
    )
    await callback.message.edit_text(text, reply_markup=_back_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu:conn")
async def cb_conn(callback: CallbackQuery, store: ConnectionStore, config: Config) -> None:
    connection = store.get_for_owner(config.owner_id)
    bcid = connection.business_connection_id if connection else "—"
    is_enabled = connection.is_enabled if connection else False
    text = (
        "🔗 Соединение\n\n"
        f"business_connection_id: {bcid}\n"
        f"is_enabled: {'да' if is_enabled else 'нет'}\n\n"
        "Как подключить:\n"
        "Настройки → Аккаунт → Автоматизация чатов → выбери бота"
    )
    await callback.message.edit_text(text, reply_markup=_back_keyboard())
    await callback.answer()


def _deleted_entry_line(cached) -> str:
    when = datetime.fromtimestamp(cached.created_at, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
    preview = cached.text or (f"[{cached.media_type}]" if cached.media_type else "(без текста)")
    if len(preview) > 60:
        preview = preview[:57] + "..."
    return f"• {when} · {cached.sender_name} · чат {cached.chat_id}\n  {preview}"


@router.callback_query(F.data == "menu:deleted")
async def cb_deleted(callback: CallbackQuery, cache: MessageCache) -> None:
    records = cache.recent_deleted(limit=10)
    if records:
        body = "\n\n".join(_deleted_entry_line(r) for r in records)
    else:
        body = "(пусто)"
    text = f"🗑 Мои удалённые\n\n{body}"
    await callback.message.edit_text(text, reply_markup=_back_keyboard())
    await callback.answer()


_EFFECT_EXAMPLES = [
    (".p", "печать по буквам"),
    (".r", "бегущая строка"),
    (".h", "глитч"),
    (".s", "пульсация (обычный/КАПС)"),
    (".f", "случайный шрифт, без анимации"),
]


@router.callback_query(F.data == "menu:effects")
async def cb_effects(callback: CallbackQuery) -> None:
    examples = "\n".join(
        f"<code>{escape(f'Привет{suffix}')}</code> — {description}"
        for suffix, description in _EFFECT_EXAMPLES
    )
    text = (
        "✨ Эффекты\n\n"
        "Допиши суффикс в конце сообщения — бот сотрёт его и применит эффект. "
        "Тапни на пример, чтобы скопировать.\n\n"
        f"{examples}\n\n"
        "Длиннее 120 символов — без анимации, придёт предупреждение в личку.\n"
        "Не больше 6 эффектов в минуту суммарно и один активный на чат — если "
        "лимит сработает, эффект пропускается и приходит уведомление.\n\n"
        "Стиль текста (жирный, курсив, шрифты и т.д.) — кнопка «🎨 Стиль» в меню."
    )
    await callback.message.edit_text(text, reply_markup=_back_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "menu:games")
async def cb_games(callback: CallbackQuery) -> None:
    text = "🎮 Игры\n\nСкоро."
    await callback.message.edit_text(text, reply_markup=_back_keyboard())
    await callback.answer()


def _exclusions_view(
    known_chats: KnownChatsStore, excluded_chats: ExcludedChatsStore
) -> tuple[str, InlineKeyboardMarkup]:
    chats = known_chats.recent(limit=MAX_EXCLUSION_CHATS_SHOWN)
    rows = []
    if chats:
        for chat in chats:
            excluded = excluded_chats.is_excluded(chat.chat_id)
            label = chat.display_name or str(chat.chat_id)
            marker = "🚫" if excluded else "✅"
            rows.append(
                [
                    InlineKeyboardButton(
                        text=f"{marker} {label}", callback_data=f"excl:toggle:{chat.chat_id}"
                    )
                ]
            )
        body = "✅ — эффект печати включён, 🚫 — выключен.\nТапни на чат, чтобы переключить."
    else:
        body = "(чатов пока нет — бот ещё не видел твоих business-переписок)"
    rows.append([InlineKeyboardButton(text="◀️ Назад", callback_data="menu:back")])
    text = f"🚫 Исключения\n\n{body}"
    return text, InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "menu:exclusions")
async def cb_exclusions(
    callback: CallbackQuery, known_chats: KnownChatsStore, excluded_chats: ExcludedChatsStore
) -> None:
    text, markup = _exclusions_view(known_chats, excluded_chats)
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data.startswith("excl:toggle:"))
async def cb_exclusions_toggle(
    callback: CallbackQuery, known_chats: KnownChatsStore, excluded_chats: ExcludedChatsStore
) -> None:
    chat_id = int(callback.data.split(":")[-1])
    if excluded_chats.is_excluded(chat_id):
        excluded_chats.include(chat_id)
    else:
        excluded_chats.exclude(chat_id)
    text, markup = _exclusions_view(known_chats, excluded_chats)
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data == "menu:back")
async def cb_back(callback: CallbackQuery, store: ConnectionStore, config: Config) -> None:
    await callback.message.edit_text(
        _main_menu_text(store, config), reply_markup=_main_menu_keyboard()
    )
    await callback.answer()
