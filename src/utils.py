from typing import List, Dict, Any

import psycopg2
import requests

from src import config


# def create_database(name_db):
#     params = db_config()
#     conn = psycopg2.connect(**params)
#     conn.autocommit = True
#     cur = conn.cursor()
#
#     cur.execute(f'DROP DATABASE IF EXISTS {name_db}')
#     cur.execute(f'DROP DATABASE IF EXISTS {name_db}')
#     cur.execute(f'CREATE DATABASE {name_db}')
#     cur.execute(f'CREATE DATABASE {name_db}')
#
#     cur.close()
#     conn.close()
#
#
# def create_tables(name_db):
#     params = db_config()
#     conn = psycopg2.connect(dbname=name_db, **params)
#     with conn:
#         with conn.cursor() as cur:
#             cur.execute("CREATE TABLE employers ("
#                         "id INT PRIMARY KEY,"
#                         "name varchar(100) NOT NULL"
#                         ")")
#             cur.execute("CREATE TABLE vacancies ("
#                         "vacancy_id SERIAL PRIMARY KEY,"
#                         "employer_id VARCHAR(20) REFERENCES employers(employer_id),"
#                         "name VARCHAR(255), NOT NULL,"
#                         "salary_from INTEGER,"
#                         "salary_to INTEGER,"
#                         "area VARCHAR,"
#                         "alternate_url TEXT"
#                         )
#
#     conn.close()
#
#
# def insert_tables(name_db):
#     hh_parser = HHParser()
#     employers = hh_parser.get_employers()
#     params = db_config()
#     conn = psycopg2.connect(dbname=name_db, **params)
#     with conn:
#         with conn.cursor() as cur:
#             for employer in employers:
#                 cur.execute("INSERT INTO employers VALUES (%s, %s)", (employer["id"], employer["name"]))
#
#     conn.close()
#
#
# def insert_tables_2(name_db):
#     hh_parser = HHParser()
#     vacancies = hh_parser.get_all_vacancies_by_employers()
#     params = db_config()
#     conn = psycopg2.connect(dbname=name_db, **params)
#     with conn:
#         with conn.cursor() as cur:
#             for vacan in vacancies:
#                 cur.execute("INSERT INTO vacancies VALUES (%s, %s, %s, %s, %s, %s,)", (
#                 vacan["id"], vacan["name"], vacan["area"], vacan["salary_from"], vacan["salary_to"],
#                 vacan["alternate_url"]))
#
#     conn.close()
def get_employer_info(employer_id: str) -> dict:
    """
    Получает информацию о работодателе по его ID.

    :param employer_id: ID работодателя на HH
    :return: словарь с данными о работодателе
    """
    url = f"https://api.hh.ru/employers/ {employer_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def save_employers_to_db(employers: List[Dict[str, Any]]) -> None:
    """ Сохраняет данные о работодателях в таблицу employers. """

    conn = psycopg2.connect(**config)
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
    conn = psycopg2.connect(**config)
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
