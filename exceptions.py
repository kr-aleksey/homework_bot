class EnvVarMissingException(Exception):
    pass


class IncorrectAPIResponseException(KeyError):
    pass


class APIUnavailableException(Exception):
    pass


class TelegramBotException(Exception):
    pass
