from aiogram import F, Router
from aiogram.filters import BaseFilter, Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from ..config import Config
from ..storage import ConnectionStore, ExcludedChatsStore

router = Router(name="commands")


class IsOwner(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, config: Config) -> bool:
        user = event.from_user
        return user is not None and user.id == config.owner_id


router.message.filter(IsOwner())
router.callback_query.filter(IsOwner())


def _main_menu_text(store: ConnectionStore, config: Config) -> str:
    connection = store.get_for_owner(config.owner_id)
    connected = connection is not None and connection[1]
    return (
        f"🤖 Бот подключён: {'да' if connected else 'нет'}\n"
        "Эффектов активно: 1\n\n"
        "Доступно:\n"
        "текст.p — печать по буквам"
    )


def _main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Эффекты", callback_data="menu:effects"),
                InlineKeyboardButton(text="Исключения", callback_data="menu:exclusions"),
            ],
            [InlineKeyboardButton(text="Статус", callback_data="menu:status")],
        ]
    )


def _back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="« Назад", callback_data="menu:back")]]
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


@router.callback_query(F.data == "menu:effects")
async def cb_effects(callback: CallbackQuery) -> None:
    text = (
        "📌 Эффекты\n\n"
        "текст.p — анимация печати по буквам.\n"
        "Напиши сообщение с суффиксом .p в конце — бот сотрёт суффикс "
        "и допечатает текст постепенно.\n\n"
        "Скорость подстраивается под длину текста:\n"
        "• до 20 символов — посимвольно\n"
        "• до 120 символов — не более 18 шагов\n"
        "• длиннее 120 символов — без анимации, придёт предупреждение в личку"
    )
    await callback.message.edit_text(text, reply_markup=_back_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu:exclusions")
async def cb_exclusions(callback: CallbackQuery, excluded_chats: ExcludedChatsStore) -> None:
    chat_ids = excluded_chats.all()
    listing = "\n".join(f"• {chat_id}" for chat_id in chat_ids) if chat_ids else "(пусто)"
    text = (
        "🚫 Исключения\n\n"
        f"{listing}\n\n"
        "В этих чатах эффект печати отключён.\n"
        "/exclude <chat_id> — добавить чат в исключения\n"
        "/include <chat_id> — убрать чат из исключений"
    )
    await callback.message.edit_text(text, reply_markup=_back_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu:status")
async def cb_status(
    callback: CallbackQuery,
    store: ConnectionStore,
    excluded_chats: ExcludedChatsStore,
    config: Config,
) -> None:
    connection = store.get_for_owner(config.owner_id)
    bcid, is_enabled = connection if connection else ("—", False)
    text = (
        "📊 Статус\n\n"
        f"business_connection_id: {bcid}\n"
        f"is_enabled: {'да' if is_enabled else 'нет'}\n"
        f"Чатов в исключениях: {len(excluded_chats.all())}"
    )
    await callback.message.edit_text(text, reply_markup=_back_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu:back")
async def cb_back(callback: CallbackQuery, store: ConnectionStore, config: Config) -> None:
    await callback.message.edit_text(
        _main_menu_text(store, config), reply_markup=_main_menu_keyboard()
    )
    await callback.answer()
