import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import APIUnavailableException, EnvVarMissingException
from exceptions import TelegramBotException
from exceptions import IncorrectAPIResponseException

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s'
)


def send_message(bot, message):
    """Отправляет сообщение в Telegram."""
    logging.debug('Отправка сообщения в Telegram.')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        raise TelegramBotException(
            f'Ошибка отправки сообщения Telegram. {error}'
        )


def get_api_answer(current_timestamp):
    """Делает запрос к API."""
    logging.debug('Отправка запроса к API.')
    params = {'from_date': current_timestamp}
    try:
        response = requests.get(ENDPOINT, params, headers=HEADERS)
    except Exception as error:
        raise APIUnavailableException(f'API недоступен. {error}')
    if response.status_code != HTTPStatus.OK:
        raise APIUnavailableException(
            f'API недоступен, код ответа сервера {response.status_code}'
        )
    return response.json()


def check_response(response):
    """Проверяет ответ API, и возвращает список домашних работ."""
    logging.debug('Проверка корректности ответа API.')
    try:
        homeworks = response['homeworks']
    except KeyError:
        raise IncorrectAPIResponseException(
            'Некорректный ответ API, на найден ключ "homeworks"'
        )
    if not isinstance(homeworks, list):
        raise IncorrectAPIResponseException(
            'Некорректный ответ API, type(homeworks) != list'
        )
    logging.debug(f'Количество домашних работ в ответе API: {len(homeworks)}')
    return homeworks


def parse_status(homework):
    """Возвращает текст сообщения о статусе проверки работы homework."""
    logging.debug('Извлечение параметров проверки работы.')
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError:
        raise IncorrectAPIResponseException
    if homework_status not in HOMEWORK_STATUSES:
        raise IncorrectAPIResponseException
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    logging.debug('Проверка доступности переменных окружения.')
    if None in (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID):
        return False
    return True


def main():
    """Основная логика работы бота."""
    logging.info('Старт программы.')
    if not check_tokens():
        errormessage = 'Отсутствует обязательная переменная окружения!'
        logging.critical(errormessage)
        raise EnvVarMissingException(errormessage)

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    current_error = None
    while True:
        try:
            response = get_api_answer(current_timestamp)
            home_works = check_response(response)
            if len(home_works) > 0:
                message = parse_status(home_works[0])
                send_message(bot, message)
            current_timestamp = response.get('current_date', current_timestamp)
        except Exception as error:
            errormessage = f'Сбой в работе программы: {error}'
            logging.critical(errormessage)
            if current_error != errormessage:
                current_error = errormessage
                send_message(bot, errormessage)
        else:
            current_error = None
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
