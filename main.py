import psycopg2

from src.config import load_config
from src.db_manager import DBManager
from src.hh_api import EMPLOYER_IDS, get_employer_vacancies, HHParser
from src.utils import get_employer_info, save_vacancies_to_db, save_employers_to_db

config = load_config()

db_manager = DBManager(config)

employers = []


def create_database(name_db):
    params = config()
    conn = psycopg2.connect(**params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f'DROP DATABASE IF EXISTS {name_db}')
    cur.execute(f'CREATE DATABASE {name_db}')

    cur.close()
    conn.close()


def create_tables(name_db):
    params = config()
    conn = psycopg2.connect(dbname=name_db, **params)
    with conn:
        with conn.cursor() as cur:
            cur.execute("CREATE TABLE employers ("
                        "id INT PRIMARY KEY,"
                        "name varchar(100) NOT NULL"
                        ")")
            cur.execute("CREATE TABLE vacancies ("
                        "vacancy_id SERIAL PRIMARY KEY,"
                        "employer_id VARCHAR(20) REFERENCES employers(employer_id),"
                        "name VARCHAR(255), NOT NULL,"
                        "salary_from INTEGER,"
                        "salary_to INTEGER,"
                        "area VARCHAR,"
                        "alternate_url TEXT"
                        )

    conn.close()


def insert_tables(name_db):
    hh_parser = HHParser()
    employers = hh_parser.get_employers()
    params = config()
    conn = psycopg2.connect(dbname=name_db, **params)
    with conn:
        with conn.cursor() as cur:
            for employer in employers:
                cur.execute("INSERT INTO employers VALUES (%s, %s)", (employer["id"], employer["name"]))

    conn.close()


def insert_tables_2(name_db):
    hh_parser = HHParser()
    vacancies = hh_parser.get_all_vacancies_by_employers()
    params = config()
    conn = psycopg2.connect(dbname=name_db, **params)
    with conn:
        with conn.cursor() as cur:
            for vacan in vacancies:
                cur.execute("INSERT INTO vacancies VALUES (%s, %s, %s, %s, %s, %s,)", (
                    vacan["id"], vacan["name"], vacan["area"], vacan["salary_from"], vacan["salary_to"],
                    vacan["alternate_url"]))

    conn.close()


def fetch_and_save_data(db_manager: DBManager):
    """Получает данные с HH и сохраняет в БД: сначала работодатели, потом вакансии."""
    employers_data = []

    for emp_id in EMPLOYER_IDS:
        employer_info = get_employer_info(emp_id)
        employers_data.append(employer_info)
        vacancies = get_employer_vacancies(emp_id)
        save_vacancies_to_db(vacancies)

    save_employers_to_db(employers_data)
    print("Данные успешно загружены в базу данных.")


def user_menu(db_manager: DBManager):
    """Меню для пользователя"""
    while True:
        print("\n========== Меню ==========")
        print("1. Вывести список компаний и количество вакансий")
        print("2. Вывести все вакансии")
        print("3. Вывести среднюю зарплату по вакансиям")
        print("4. Вывести вакансии с зарплатой выше средней")
        print("5. Найти вакансии по ключевому слову")
        print("0. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            result = db_manager.get_companies_and_vacancies_count()
            print("\nКомпании и количество вакансий:")
            for name, count in result:
                print(f"{name}: {count}")

        elif choice == "2":
            result = db_manager.get_all_vacancies()
            print("\nВсе вакансии:")
            for item in result:
                print(item)

        elif choice == "3":
            avg_salary = db_manager.get_avg_salary()
            print(f"\nСредняя зарплата по всем вакансиям: {avg_salary:.2f} руб.")

        elif choice == "4":
            result = db_manager.get_vacancies_with_higher_salary()
            print("\nВакансии с зарплатой выше средней:")
            for item in result:
                print(item)

        elif choice == "5":
            keyword = input("Введите ключевое слово для поиска вакансий: ")
            result = db_manager.get_vacancies_with_keyword(keyword)
            print(f"\nВакансии с ключевым словом '{keyword}':")
            for item in result:
                print(item)

        elif choice == "0":
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    db_config = load_config()

    db_manager = DBManager(db_config)

    update_data = input("Обновить данные в БД? (y/n): ").lower()
    if update_data == "y":
        fetch_and_save_data(db_manager)

    user_menu(db_manager)
