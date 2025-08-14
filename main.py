import psycopg2

from src.config import load_config
from src.db_manager import DBManager
from src.hh_api import EMPLOYER_IDS, get_employer_vacancies
from src.utils import save_vacancies_to_db, save_employers_to_db, get_employer_info


def create_database(db_name: str, config: dict):
    """Создаёт базу данных."""
    conn = psycopg2.connect(**config)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f'DROP DATABASE IF EXISTS {db_name}')
    cur.execute(f'CREATE DATABASE {db_name}')

    cur.close()
    conn.close()


def create_tables(db_name: str, config: dict):
    """Создаёт таблицы employers и vacancies."""
    conn = psycopg2.connect(dbname=db_name, **config)
    with conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE employers (
                    employer_id VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    open_vacancies INTEGER
                )
            ''')

            cur.execute('''
                CREATE TABLE vacancies (
                    vacancy_id SERIAL PRIMARY KEY,
                    employer_id VARCHAR(20) REFERENCES employers(employer_id),
                    name VARCHAR(255) NOT NULL,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    currency VARCHAR(10),
                    area VARCHAR(100),
                    url TEXT
                )
            ''')
    conn.close()


def fetch_and_save_data(db_name: str, config: dict):
    """Получает данные по EMPLOYER_IDS и сохраняет в БД."""
    employers_data = []
    vacancies_data = []

    for emp_id in EMPLOYER_IDS:
        employer_info = get_employer_info(emp_id)
        if employer_info:
            employers_data.append({
                "id": employer_info["id"],
                "name": employer_info["name"],
                "open_vacancies": employer_info.get("open_vacancies", 0)
            })

            vacancies = get_employer_vacancies(emp_id)
            for vacancy in vacancies:
                salary = vacancy.get("salary")
                salary_from = salary["from"] if salary and salary["from"] else None
                salary_to = salary["to"] if salary and salary["to"] else None
                currency = salary["currency"] if salary and salary["currency"] else None

                vacancies_data.append({
                    "employer_id": vacancy["employer"]["id"],
                    "name": vacancy["name"],
                    "salary_from": salary_from,
                    "salary_to": salary_to,
                    "currency": currency,
                    "area": vacancy["area"]["name"] if vacancy["area"] else None,
                    "url": vacancy["alternate_url"]
                })

    save_employers_to_db(employers_data)
    save_vacancies_to_db(vacancies_data)
    print("Данные успешно загружены в базу данных.")


def user_menu(db_manager: DBManager):
    """Меню для пользователя."""
    while True:
        print("\n========== Меню ==========")
        print("1. Список компаний и количество вакансий")
        print("2. Все вакансии")
        print("3. Средняя зарплата")
        print("4. Вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("0. Выход")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            result = db_manager.get_companies_and_vacancies_count()
            print("\nКомпании и количество вакансий:")
            for name, count in result:
                print(f"{name}: {count}")

        elif choice == "2":
            result = db_manager.get_all_vacancies()
            print("\nВсе вакансии:")
            for company, title, sal_from, sal_to, currency, url in result:
                print(f"{company} — {title}: {sal_from}-{sal_to} {currency or 'не указана'} → {url}")

        elif choice == "3":
            avg_salary = db_manager.get_avg_salary()
            print(f"\nСредняя зарплата: {avg_salary:,.0f} руб.")

        elif choice == "4":
            result = db_manager.get_vacancies_with_higher_salary()
            print("\nВакансии с зарплатой выше средней:")
            for company, title, avg_sal, url in result:
                print(f"{company} — {title}: {avg_sal:,.0f} → {url}")

        elif choice == "5":
            keyword = input("Введите ключевое слово: ").strip()
            if not keyword:
                print("Ключевое слово не может быть пустым.")
                continue
            result = db_manager.get_vacancies_with_keyword(keyword)
            print(f"\nРезультаты по запросу '{keyword}':")
            for company, title, sal_from, sal_to, url in result:
                print(f"{company} — {title}: {sal_from}-{sal_to} → {url}")

        elif choice == "0":
            print("Выход из программы.")
            break

        else:
            print("Неверный ввод. Попробуйте снова.")


if __name__ == "__main__":
    config = load_config()
    db_name = "hh_db"
    update_data = input("Обновить данные в БД? (y/n): ").strip().lower()
    if update_data == "y":
        print("Создание базы данных...")
        create_database(db_name, config)

        print("Создание таблиц...")
        create_tables(db_name, config)

        print("Получение и сохранение данных с HH.ru...")
        fetch_and_save_data(db_name, config)

    db_config_with_db = {**config, "dbname": db_name}
    db_manager = DBManager(db_config_with_db)
    user_menu(db_manager)
