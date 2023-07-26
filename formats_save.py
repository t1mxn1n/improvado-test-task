import csv
import json
import os


def save_general(format_report: str, path_report: str, result: list) -> str:
    """
    Функция проверяет валидность путя сохранения при его наличии,
    и сохраняет по указанному типу сохраняемого файла.
    :param format_report: Формат сохраняемого файла
    :param path_report: Путь сохранения
    :param result: Данные для сохранения
    :return:
    """
    if path_report and path_report[-1] != '\\':
        path_report += '\\'

    path_save = f'{path_report}report.{format_report}'
    # Проверка на существование путя, который ввёл пользователь
    if path_report and not os.path.exists(path_report):
        print('[warning] invalid path for save, report will be saved in current directory...')
        path_save = f'report.{format_report}'

    # Проверка на доступность указанного путя
    if path_report != f'report.{format_report}' and not os.access(path_save, os.W_OK):
        print(f'[warning] you dont have permissions to save in {path_save}, report will be saved in current directory')
        path_save = f'report.{format_report}'

    match format_report:
        case 'csv':
            saved_path = save_csv_tsv(result, 'csv', path_save)
        case 'tsv':
            saved_path = save_csv_tsv(result, 'tsv', path_save)
        case 'json':
            saved_path = save_json(result, path_save)
        case _:
            saved_path = save_csv_tsv(result, 'csv', path_save)
    return saved_path


def save_json(data: list, path: str) -> str:
    """
    Функция сохранения json формата.
    :param data: Сохраняемые данные
    :param path: Путь сохранения
    :return: Путь по которому был сохранен файл
    """
    json_data = json.dumps({'friends': data}, ensure_ascii=False)
    with open(path, 'w', encoding='utf-8') as json_file:
        json_file.write(json_data)
    return os.path.abspath(path)


def save_csv_tsv(data: list, type_save: str, path: str) -> str:
    """
    Функция сохранения csv, tsv формата
    :param data: Сохраняемые данные
    :param type_save: Тип csv или tsv
    :param path: Путь сохранения
    :return: Путь по которому был сохранен файл
    """
    with open(path, 'w', encoding='utf-8') as file:
        if type_save == 'csv':
            delimiter = ','
        if type_save == 'tsv':
            delimiter = '\t'
        writer = csv.DictWriter(file, fieldnames=data[0].keys(), delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data)
    return os.path.abspath(path)
