class MissingTokenError(Exception):
    """Не найден один из необходимых токенов."""


class NetworkError(Exception):
    """Ошибка при подключении к API."""


class BadJSONFromAPIError(Exception):
    """API-запрос вернул некорректно составленный JSON."""
