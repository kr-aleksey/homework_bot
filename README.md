# Homework bot
## Python Telegram bot-assistant
### Стек: Python, python-telegram-bot, requests

Homework bot получает статус ревью домашнего задания через Yandex Practicum API. Сообщения об изменениях статусов ревью присылает в Telegram.
В проекте реализовано логирование ошибок и событий. Сообщения об ошибках ЯП API также отправляются в Telegram.

## Запуск проекта
* Клонируйте репозиторий и перейдите в папку проекта:
```
git clone https://github.com/kr-aleksey/homework_bot.git
cd homework_bot
```

* Создайте и активируйте виртуальное окружение:
```
python3 -m venv venv
source venv/bin/activate
```

* Установите зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

* Создайте файл .env, введите значения переменных среды по образцу в .env.example:
```
nano .env
```

* Запустите бот:
```
python3 homework.py
```


Автор - Алексей Кравцун

mailto: kravtsun.aleksey@gmail.com
