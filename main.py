import requests
from requests.models import Response
from loguru import logger

from formats_save import save_general
API_V = 5.131

logger.remove()
logger.add('debug.log', format='{time} {level} {message}',
           level='DEBUG', rotation='10 MB')


def add_zero(number: str) -> str:
    """
    Добавление 0 для односимвольного числа.
    :param number: Входное число
    :return: Число, состоящее из двух символов
    """
    if len(number) == 1:
        number = '0' + number
    return number


def convert_to_iso(data: str) -> str:
    """
    Преобразование даты в ISO формат.
    :param data: Стока формата 1.5 или 5.10.1999
    :return: Дату в ISO формате
    """
    numbers = data.split('.')
    numbers[0] = add_zero(numbers[0])
    numbers[1] = add_zero(numbers[1])

    if len(numbers) == 2:
        # dd.mm -> MM-DD
        return f'{numbers[1]}-{numbers[0]}'
    if len(numbers) == 3:
        # dd.mm.yyyy -> YYYY-MM-DD
        return f'{numbers[2]}-{numbers[1]}-{numbers[0]}'


def check_field(data: dict, field: str) -> str:
    """
    Проверка на наличие поля в полученных данных.
    :param data: Данные по аккаунту
    :param field: Проверяемое поле
    :return: Значение поля или 'no_data'
    """
    if data.get(field):
        if field in ['city', 'country']:
            return data[field]['title']
        if field == 'bdate':
            return convert_to_iso(data[field])
        return data[field]
    return 'no data'


def define_sex(code: int) -> str:
    """
    Определение гендера по коду.
    :param code: Код гендера
    :return: Определенный гендер
    """
    match code:
        case 1:
            return 'ж'
        case 2:
            return 'м'
        case _:
            return '-'


def account_info(access_token: str, user_id: str) -> (str, bool):
    """
    Получение идентификатора аккаунта по screen_name.
    :param access_token: Авторизованный ключ доступа
    :param user_id: Идентификатор пользователя
    :return: ID пользователя и булевое значение (id получен -> true, иначе -> false)
    """
    response = requests.post('https://api.vk.com/method/users.get', params={
        'user_ids': user_id,
        'access_token': access_token,
        'v': API_V,
        'fields': 'bdate'
    })
    response_json = response.json()
    if len(response_json['response']) > 0:
        return response_json['response'][0]['id'], True
    return user_id, False


def get_friends_by_offset(access_token: str, user_id: str, offset: int) -> Response:
    """
    Получение списка друзей с заданным смещением.
    :param access_token: Авторизованный ключ доступа
    :param user_id: Идентификатор аккаунта
    :param offset: Смещение
    :return: Ответ VK API
    """
    response = requests.post('https://api.vk.com/method/friends.get', params={
        'offset': offset,
        'user_id': user_id,
        'fields': 'country,city,sex,bdate',
        'access_token': access_token,
        'v': API_V
    })
    return response


def get_result(access_token: str, user_id: str) -> None | list:
    """
    Получение данных, проверка на наличие более 5000 друзей,
    форматирование полей словаря.
    :param access_token: Авторизованный ключ доступа
    :param user_id: Идентификатор аккаунта
    :return: None, если данные не получены, иначе список словарей с информацией
    """
    # Если поданный ID не является числом, то необходимо получить численное значение ID
    if not user_id.isnumeric():
        user_id = account_info(access_token, user_id)[0]
    request_1 = requests.post('https://api.vk.com/method/friends.get', params={
        'user_id': user_id,
        'order': 'name',
        'fields': 'country,city,sex,bdate',
        'access_token': access_token,
        'v': API_V
    })

    if request_1.json().get('error'):
        logger.error(f' user_id: {user_id} | msg: {request_1.json()["error"]["error_msg"]}')
        print(f'[error] {request_1.json()["error"]["error_msg"]}')
        return None

    # Количество друзей, полученных из запроса с параметом field (для дальнейшей проверки на 5000 друзей)
    count_friends_fields = request_1.json()['response']['count']
    friends_response = []
    if count_friends_fields == 0:
        print(f'[error] user {user_id} have 0 friends')
        return None
    if count_friends_fields == 5000:
        request_2 = requests.post('https://api.vk.com/method/friends.get', params={
            'user_id': user_id,
            'order': 'name',
            'access_token': access_token,
            'v': API_V
        })
        real_count_friends = request_2.json()['response']['count']
        if real_count_friends > 5000:
            print(f'[info] this account have {real_count_friends} friends, data collection will take some time...')
            # Максимум друзей 10000, поэтому достаточно два запроса для получения полного списка
            part_1 = get_friends_by_offset(access_token, user_id, 0)
            part_2 = get_friends_by_offset(access_token, user_id, 5000)
            temp_res = part_1.json()['response']['items'] + part_2.json()['response']['items']
            # Сортировка по имени
            friends_response = sorted(temp_res, key=lambda d: d['first_name'])

    if not friends_response:
        friends_response = request_1.json()['response']['items']


    result = []
    # Преобразование полей для удобного вида
    for friend in friends_response:
        result.append({
            'Имя': friend['first_name'],
            'Фамилия': friend['last_name'],
            'Страна': check_field(friend, 'country'),
            'Город': check_field(friend, 'city'),
            'Дата рождения': check_field(friend, 'bdate'),
            'Пол': define_sex(friend['sex']),
        })
    return result


def check_correct_token(access_token: str) -> bool:
    """
    Проверка ключа доступа VK API.
    :param access_token: Авторизованный ключ доступа
    :return: Если ключ валидный -> true, иначе -> false
    """
    response = requests.post('https://api.vk.com/method/account.getInfo', params={
        'access_token': access_token,
        'v': API_V
    })
    if response.json().get('error'):
        logger.error(f'token: {access_token} | msg: {response.json()["error"]["error_msg"]}')
        return False
    return True


if __name__ == '__main__':
    # Так как токен и идентификатор пользователя обязательные, то
    # они будут вводиться пока не будет введен корректный вариант
    token = input('Enter access token (required): ')
    while not check_correct_token(token):
        print('[error] invalid token, try again...')
        token = input('Enter access token (required): ')

    user_id = input('Enter user id (required): ')
    while not account_info(token, user_id)[1]:
        print('[error] invalid user id, try again...')
        user_id = input('Enter user id (required): ')

    result = get_result(token, user_id)
    if result is None:
        print('Program closed...')
        quit()

    print(f'[info] Account data {user_id} has been received. Choose params for save report...')

    format_report = input('Enter format of report file (csv, tsv, json). For default value `csv` press Enter: ')
    if not format_report:
        format_report = 'csv'
    if format_report not in ['csv', 'tsv', 'json']:
        print(f'[warning] Undefined format `{format_report}`, was selected default format `csv`')
        format_report = 'csv'

    path_report = input('Enter path to save report. Press Enter for save in current directory: ')
    if not path_report:
        path_report = ''

    saved_path = save_general(format_report, path_report, result)
    print(f'saved to {saved_path}')
