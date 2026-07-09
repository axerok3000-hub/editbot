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
   дописывает текст небольшими порциями с задержкой — получается эффект
   печати. В конце в чате остаётся текст без суффикса: `Привет`.

Всё остальное (сообщения без суффикса, сообщения от собеседника, любые
чужие апдейты) полностью игнорируется.

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
```

Остальные параметры (`TYPEWRITER_SUFFIX`, `TYPEWRITER_CHUNK_SIZE`,
`TYPEWRITER_DELAY_MS`) можно оставить по умолчанию.

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

## Структура

```
main.py            точка входа, long polling
bot/config.py       загрузка настроек из .env
bot/storage.py       хранение business_connection_id -> owner_id (storage/connections.json)
bot/typewriter.py    построчная (посимвольная) анимация через edit_message_text
bot/handlers.py      обработчики business_connection и business_message
```
