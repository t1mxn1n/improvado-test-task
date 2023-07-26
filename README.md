# improvado-test-task
## Описание
Improvado Back-end test task for Junior Developer: VK get friends report (2023)

## Применение
Можно использовать в качестве стороннего модуля сервисов/приложений для получения друзей VK.

## Установка
1. Скачать Python версии 3.11 или выше с сайта https://www.python.org/downloads/ 
2. Установить скачанный файл (при установке нужно будет выбрать чекпоинт с надписью Add Python to PATH, затем нажать далее) 
3. Клонировать данный репозиторий к себе на компьютер в выбранную вами папку консольной командой `git clone https://github.com/t1mxn1n/improvado-test-task.git`
4. В консоли перейти в каталог склонированного проекта и командой pip install -r requirements.txt скачать необходимые библиотеки
5. Запуск консольного приложения `python.exe .\main.py` (в случае нахождения в текущей директории)

## Получение авторизованного токена
1. Регстрация приложения (гайд по [ссылке](https://dev.vk.com/api/getting-started#Регистрация%20приложения))
2. В найстройках зарегестрированного приложения включить `Open API` и указать адресс сайта и базовый домен как `localhost`
3. В настройках приложения поменять `Состояние` на `Приложение включено и видно всем`
4. Сформировать запрос, указав ID приложения, получать в настройках приложения
>https://oauth.vk.com/authorize?client_id=XXXXXXX&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends,offline&response_type=token&v=5.131&revoke=1

## Использованные VK API эндпоинты
* `users.get` используется для получения информации о пользователях, в данной работе используется для получения числового идентификатора пользователя
* `friends.get` используется для получения списка друзей, в работе используется два варианта использования, с параметром `fields` (до 5000 друзей, сортировка по полю `name`), и без него (от 5000 друзей)
* `account.getInfo` возвращает информацию об аккаунте, в работе используется для проверки валидности введенного пользователем ключа доступа
