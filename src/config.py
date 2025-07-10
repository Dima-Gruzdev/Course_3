import configparser
import os
from typing import Dict


def load_config(filename="database.ini", section="postgresql") -> Dict[str, str]:
    """ Читает конфигурационный файл и возвращает параметры подключения к БД."""

    if not os.path.exists(filename):
        raise FileNotFoundError(f"Файл конфигурации '{filename}' не найден.")
    parser = configparser.ConfigParser()
    parser.read(filename, encoding='utf-8-sig')

    if not parser.has_section(section):
        raise ValueError(f"Секция [{section}] не найдена в файле {filename}")

    config = dict(parser.items(section))

    required_keys = ['dbname', 'user', 'password', 'host', 'port']
    for key in required_keys:
        if key not in config:
            raise KeyError(f"В секции [{section}] отсутствует обязательный параметр: {key}")

    return config
