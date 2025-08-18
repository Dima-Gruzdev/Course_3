from typing import List, Dict, Any

import psycopg2
import requests

from src.config import load_config


def get_employer_info(employer_id: str) -> dict:
    """
    Получает информацию о работодателе по его ID.

    :param employer_id: ID работодателя на HH
    :return: словарь с данными о работодателе
    """
    url = f"https://api.hh.ru/employers/{employer_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def save_employers_to_db(employers: List[Dict[str, Any]]) -> None:
    """ Сохраняет данные о работодателях в таблицу employers. """

    conn = psycopg2.connect(**load_config())
    with conn.cursor() as cur:
        for employer in employers:
            cur.execute(
                """
                INSERT INTO employers (employer_id, name, open_vacancies)
                VALUES (%s, %s, %s)
                ON CONFLICT (employer_id) DO NOTHING
                """,
                (employer["id"], employer["name"], employer["open_vacancies"])
            )
        conn.commit()


def save_vacancies_to_db(vacancies: List[Dict[str, Any]]) -> None:
    """ Сохраняет данные о вакансиях в таблицу vacancies. """
    conn = psycopg2.connect(**load_config())
    with conn.cursor() as cur:
        for vacancy in vacancies:
            salary = vacancy.get("salary")
            if salary:
                salary_from = salary.get("from")
                salary_to = salary.get("to")
                currency = salary.get("currency")
            else:
                salary_from = salary_to = currency = None

            cur.execute(
                """
                INSERT INTO vacancies (employer_id, name, salary_from, salary_to, currency, url)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    vacancy["employer"]["id"],
                    vacancy["name"],
                    salary_from,
                    salary_to,
                    currency,
                    vacancy["alternate_url"]
                )
            )
        conn.commit()
