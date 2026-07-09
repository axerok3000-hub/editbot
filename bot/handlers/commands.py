from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import BaseFilter, Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from ..config import Config
from ..db import MessageCache
from ..storage import ConnectionStore, ExcludedChatsStore

router = Router(name="commands")


class IsOwner(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, config: Config) -> bool:
        user = event.from_user
        return user is not None and user.id == config.owner_id


router.message.filter(IsOwner())
router.callback_query.filter(IsOwner())


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
        "Эффектов: 1"
    )


def _main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 Профиль", callback_data="menu:profile"),
                InlineKeyboardButton(text="🔗 Соединение", callback_data="menu:conn"),
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


def _parse_chat_id_arg(message: Message) -> int | None:
    if not message.text:
        return None
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        return None
    try:
        return int(parts[1].strip())
    except ValueError:
        return None


@router.message(CommandStart())
async def cmd_start(message: Message, store: ConnectionStore, config: Config) -> None:
    await message.answer(_main_menu_text(store, config), reply_markup=_main_menu_keyboard())


@router.message(Command("exclude"))
async def cmd_exclude(message: Message, excluded_chats: ExcludedChatsStore) -> None:
    chat_id = _parse_chat_id_arg(message)
    if chat_id is None:
        await message.answer("Использование: /exclude <chat_id>")
        return
    excluded_chats.exclude(chat_id)
    await message.answer(f"Чат {chat_id} добавлен в исключения.")


@router.message(Command("include"))
async def cmd_include(message: Message, excluded_chats: ExcludedChatsStore) -> None:
    chat_id = _parse_chat_id_arg(message)
    if chat_id is None:
        await message.answer("Использование: /include <chat_id>")
        return
    excluded_chats.include(chat_id)
    await message.answer(f"Чат {chat_id} убран из исключений.")


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


@router.callback_query(F.data == "menu:effects")
async def cb_effects(callback: CallbackQuery) -> None:
    text = "✨ Эффекты\n\nтекст.p — печать по буквам"
    await callback.message.edit_text(text, reply_markup=_back_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu:games")
async def cb_games(callback: CallbackQuery) -> None:
    text = "🎮 Игры\n\nСкоро."
    await callback.message.edit_text(text, reply_markup=_back_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu:back")
async def cb_back(callback: CallbackQuery, store: ConnectionStore, config: Config) -> None:
    await callback.message.edit_text(
        _main_menu_text(store, config), reply_markup=_main_menu_keyboard()
    )
    await callback.answer()
