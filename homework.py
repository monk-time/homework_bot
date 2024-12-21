# ruff: noqa: BLE001

import logging
import os
import sys
import time
from http import HTTPStatus
from json import JSONDecodeError

import requests
import telegram
from dotenv import load_dotenv

from exceptions import BadJSONFromAPIError, MissingTokenError, NetworkError

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600  # в секундах
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# По техзаданию логирование должно вестись в терминал, а не в файл
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] '
    '%(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """Проверить доступность переменных окружения, необходимых для работы."""
    token_names = ('PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')
    missing_tokens = [name for name in token_names if not globals().get(name)]
    if missing_tokens:
        message = f'В окружении не найдены токены {", ".join(missing_tokens)}'
        logger.critical(message)
        raise MissingTokenError(message)
    logger.info('Все токены успешно найдены в переменных окружения')


def send_message(bot, message: str) -> None:
    """Отправить сообщение в Telegram чат TELEGRAM_CHAT_ID."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception:
        logger.exception('Ошибка отправки сообщения боту в Telegram')
        return
    logger.debug('Успешно отправлено сообщение боту в Telegram')


def get_api_answer(timestamp: int) -> dict:
    """Сделать запрос к API Яндекс.Практикума и получить ответ о статусе."""
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp},
        )
    except Exception as error:
        msg = f'Сбой при запросе к Яндекс.Практикуму: {error}'
        raise NetworkError(msg) from error
    if homework_statuses.status_code != HTTPStatus.OK:
        msg = (
            f'API Яндекс.Практикума вернул код {homework_statuses.status_code}'
        )
        raise requests.HTTPError(msg)
    try:
        api_answer = homework_statuses.json()
    except JSONDecodeError as error:
        msg = f'Сервер вернул невалидный JSON: {error}'
        raise BadJSONFromAPIError(msg) from error
    logger.debug('Успешно получен ответ от API Яндекс.Практикума')
    return api_answer


def check_response(response: dict) -> None:
    """Проверить ответ API на соответствие документации."""
    if not isinstance(response, dict):
        msg = f'Ответ API является не словарем, а {type(response)}'
        raise TypeError(msg)
    for key in ('current_date', 'homeworks'):
        if key not in response:
            msg = f"В ответе API нет ключа '{key}'"
            raise BadJSONFromAPIError(msg)
    if not isinstance(response['homeworks'], list):
        msg = (
            "В ответе API под ключом 'homeworks' лежит не список, "
            f'а {type(response["homeworks"])}'
        )
        raise TypeError(msg)
    logger.debug('Ответ API корректен')


def parse_status(homework: dict) -> str:
    """Извлечь из информации о конкретной домашней работе её статус."""
    try:
        homework_name = homework['homework_name']
        status = homework['status']
    except KeyError as error:
        msg = f'В ответе API нет ключа {error}'
        raise BadJSONFromAPIError(msg) from error
    if status not in HOMEWORK_VERDICTS:
        msg = f'Неожиданный статус домашней работы: {status}'
        raise BadJSONFromAPIError(msg)
    return (
        f'Изменился статус проверки работы "{homework_name}". '
        f'{HOMEWORK_VERDICTS[status]}'
    )


def main():
    """Основная логика работы бота."""
    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    previous_message = None

    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            homeworks = response['homeworks']
            if homeworks:
                status = parse_status(homeworks[0])
                logger.info(f'Обнаружено новое обновление статуса: {status}')
                send_message(bot, status)
            else:
                logger.debug('Нет новых обновлений статуса')
            timestamp = response['current_date']
            previous_message = None
        except Exception as error:
            message = str(error)
            logger.exception(message)
            if message != previous_message:
                send_message(bot, message)
            previous_message = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
