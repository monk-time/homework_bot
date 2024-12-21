# homework_bot
Telegram-бот для проверки статуса домашней работы на сервисе Практикум.Домашка.

При обновлении статуса последней работы бот присылает уведомление в указанный чат. Логирование ведётся в stdout.

### Используемые технологии
- Python 3.12
- python-telegram-bot
- python-dotenv
- requests
- uv

### Запуск бота
1. Создать файл `.env` с переменными окружения:
    - `PRACTICUM_TOKEN` - токен API сервиса Практикум.Домашка
    - `TELEGRAM_TOKEN` - токен Telegram-бота
    - `TELEGRAM_CHAT_ID` - ID чата адресата оповещения

2. Подготовить окружение и запустить скрипт:
    ```bash
    uv run homework.py
    ```

### Об авторе
Дмитрий Богорад [@monk-time](https://github.com/monk-time).
