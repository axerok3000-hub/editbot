# editbot

Telegram Business Bot, который анимирует эффект печатной машинки для твоих
собственных исходящих сообщений в личных чатах.

Бот не общается с пользователями и не реагирует на чужие сообщения. Он
подключается к твоему аккаунту как Business Bot и следит только за
сообщениями, которые отправляешь ты сам.

## Как это работает

1. Ты подключаешь бота в Telegram: **Settings → Telegram Business → Chatbots**.
   Бот получает апдейт `business_connection` — сохраняет `business_connection_id`
   и id владельца аккаунта.
2. Ты пишешь в любом личном чате сообщение с суффиксом `.p`, например:
   `Привет.p`
3. Бот ловит апдейт `business_message`, видит, что отправитель — владелец
   подключения, и что текст оканчивается на `.p`.
4. Через `edit_message_text` (с `business_connection_id`) бот постепенно
   дописывает текст — получается эффект печати. В конце в чате остаётся
   текст без суффикса: `Привет`. Скорость подстраивается под длину текста
   (см. `bot/typewriter.py`): до 20 символов — посимвольно, до 120 — не
   более 18 шагов, длиннее — без анимации плюс предупреждение тебе в личку.

Всё остальное (сообщения без суффикса, сообщения от собеседника, чаты из
списка исключений, любые чужие апдейты) полностью игнорируется.

В личном чате с самим ботом (не через business, а напрямую) доступны
команды `/start` (меню с инлайн-кнопками «Эффекты» / «Исключения» /
«Статус»), `/exclude <chat_id>` и `/include <chat_id>`. Реагирует на них
только `OWNER_ID` — все остальные отправители молча игнорируются.

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заполни `.env`:

```
BOT_TOKEN=<токен от @BotFather>
OWNER_ID=<твой Telegram user_id>
```

Узнать свой `user_id` можно, например, у [@userinfobot](https://t.me/userinfobot).
Остальные параметры (`TYPEWRITER_SUFFIX`, `CONNECTIONS_FILE`,
`EXCLUDED_CHATS_FILE`) можно оставить по умолчанию.

## Подключение бота как Business Bot

1. Создай бота через [@BotFather](https://t.me/BotFather), если ещё нет.
2. В Telegram: **Settings → Telegram Business → Chatbots** → выбери своего
   бота.
3. Включи право читать сообщения ("Reply to messages" не обязательно, но
   должно быть включено "Can read messages" — иначе бот не увидит текст
   входящих `business_message`, а без этого не сработает и распознавание
   твоих собственных исходящих сообщений).

## Запуск

```bash
python main.py
```

Бот работает через long polling — процесс должен быть постоянно запущен
(systemd, screen/tmux, Docker и т.п.).

## Деплой на Railway

Бот — фоновый воркер (long polling), HTTP-порт не нужен. Всё делается через
веб-интерфейс Railway, можно с телефона.

1. Зайди на [railway.app](https://railway.app) → **New Project** →
   **Deploy from GitHub repo** → выбери `axerok3000-hub/editbot`
   (ветку `claude/telegram-typewriter-bot-melhq5`, или замерджи её в main).
2. Railway распознает `railway.json`/`Procfile` и сам поставит команду
   запуска `python main.py`. Порт открывать не нужно — сервис фоновый.
3. Открой сервис → **Variables** → добавь:
   - `BOT_TOKEN` — токен от @BotFather
   - `OWNER_ID` — твой Telegram user_id
   - `CONNECTIONS_FILE` = `/data/connections.json`
   - `EXCLUDED_CHATS_FILE` = `/data/excluded_chats.json`
4. Добавь постоянное хранилище: сервис → **Settings → Volumes** →
   **New Volume**, mount path `/data`. Это важно: без volume файл
   `connections.json` будет стираться при каждом передеплое, и после
   рестарта бот "забудет" про business-подключение, пока ты не переподключишь
   его заново в настройках Telegram.
5. **Deploy**. В логах сервиса должно появиться `Start polling`.
6. Подключи бота в Telegram как Business Bot (см. раздел выше) — придёт
   апдейт `business_connection`, бот сохранит его в `/data/connections.json`.

Обновления кода: просто пушь в подключённую ветку — Railway передеплоит
автоматически.

## Структура

```
main.py                     точка входа, long polling
bot/config.py                загрузка настроек из .env
bot/storage.py                хранение business-подключений и списка исключений
bot/typewriter.py             адаптивная анимация печати через edit_message_text
bot/handlers/business.py      обработчики business_connection и business_message
bot/handlers/commands.py      /start, /exclude, /include и инлайн-меню (только OWNER_ID)
```
