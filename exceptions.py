class MissingTokenError(Exception):
    """Не найден один из необходимых токенов."""

    pass


class NetworkError(Exception):
    """Ошибка при подключении к API."""

    pass


class BadJSONFromAPIError(Exception):
    """API-запрос вернул некорректно составленный JSON."""

    pass
