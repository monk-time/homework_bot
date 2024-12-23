import os
import sys
from pathlib import Path

import pytest
import pytest_timeout

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

BASE_DIR = Path(__file__).resolve().parent.parent
HOMEWORK_FILENAME = 'homework.py'
# проверяем, что в корне репозитория лежит файл с домашкой
if not (BASE_DIR / HOMEWORK_FILENAME).is_file():
    pytest.fail(
        f'В директории `{BASE_DIR}` не найден файл '
        f'с домашней работой `{HOMEWORK_FILENAME}`. '
    )

pytest_plugins = ['tests.fixtures.fixture_data']

TIMEOUT_ASSERT_MSG = (
    'Проект работает некорректно, проверка прервана.\n'
    'Вероятные причины ошибки:\n'
    '1. Исполняемый код (например, вызов функции `main()`) оказался в '
    'глобальной зоне видимости. Как исправить: закройте исполняемый код '
    'конструкцией `if __name__ == "__main__":`\n'
    '2. Инструкция `time.sleep()` в цикле `while True` в функции `main()` при '
    'каких-то условиях не выполняется. Как исправить: измените код так, чтобы '
    'эта инструкция выполнялась при любом сценарии выполнения кода.'
)


def write_timeout_reasons(text, stream=None):
    """Write possible reasons of tests timeout to stream.

    The function to replace pytest_timeout traceback output with possible
    reasons of tests timeout.
    Appears only when `thread` method is used.
    """
    if stream is None:
        stream = sys.stderr
    text = TIMEOUT_ASSERT_MSG
    stream.write(text)


pytest_timeout.write = write_timeout_reasons

os.environ['PRACTICUM_TOKEN'] = 'sometoken'
os.environ['TELEGRAM_TOKEN'] = '1234:abcdefg'
os.environ['TELEGRAM_CHAT_ID'] = '12345'
