from typing import List, Tuple, Optional

import psycopg2


class DBManager:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """ получает список всех компаний и количество вакансий у каждой компании. """

        with self.conn.cursor() as cur:
            cur.execute("SELECT name, open_vacancies FROM employers")
            return cur.fetchall()

    def get_all_vacancies(self) -> List[Tuple[str, str, Optional[int], Optional[int], Optional[str], str]]:
        """ получает список всех вакансий
         с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию.
        """

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT e.name, v.name, v.salary_from, v.salary_to, v.currency, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
            """)
            return cur.fetchall()

    def get_avg_salary(self) -> float:
        """ получает среднюю зарплату по вакансиям. """

        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT AVG((salary_from + salary_to)/2) FROM vacancies WHERE "
                "salary_from IS NOT NULL AND salary_to IS NOT NULL")
            return cur.fetchone()[0]

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, str, float, str]]:
        """ получает список всех вакансий, у которых зарплата выше средней по всем вакансиям. """

        avg_salary = self.get_avg_salary()
        with self.conn.cursor() as cur:
            cur.execute(f"""
                SELECT e.name, v.name, (v.salary_from + v.salary_to)/2 AS avg_salary, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE (v.salary_from + v.salary_to)/2 > {avg_salary}
            """)
            return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        """ получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python. """

        with self.conn.cursor() as cur:
            cur.execute(f"""
                SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE v.name ILIKE '%{keyword}%';
            """)
            return cur.fetchall()
