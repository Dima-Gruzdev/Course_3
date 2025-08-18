import requests

EMPLOYER_IDS = [
    "15478",  # Яндекс
    "4934",  # Ростелеком
    "78638",  # Тинькофф
    "1057",  # Авито
    "2180",  # Ozon
    "1423",  # VK
    "3529",  # Сбер
    "1122462",  # Skyeng
    "870471",  # Wildberries
    "24592"  # МТС PJSC
]


class HHParser:
    def __init__(self):
        self.employer_url = 'https://api.hh.ru/employers'
        self.vacancies_url = 'https://api.hh.ru/vacancies'

    def get_employer_info(self, employer_id: str) -> dict:
        """Получает информацию о работодателе по ID."""
        url = f"{self.employer_url}/{employer_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении данных о работодателе {employer_id}: {e}")
            return {}

    def get_vacancies_by_employer(self, employer_id: str) -> list:
        """Получает вакансии работодателя по ID."""
        params = {"employer_id": employer_id, "per_page": 100}
        try:
            response = requests.get(self.vacancies_url, params=params)
            response.raise_for_status()
            return response.json().get("items", [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении вакансий для {employer_id}: {e}")
            return []

    def get_all_employers(self) -> list:
        """Возвращает список нужных работодателей."""
        employers = []
        for emp_id in EMPLOYER_IDS:
            info = self.get_employer_info(emp_id)
            if info:
                employers.append({
                    "id": info["id"],
                    "name": info["name"],
                    "open_vacancies": info.get("open_vacancies", 0)
                })
        return employers

    def get_all_vacancies(self) -> list:
        """Получает все вакансии для всех указанных работодателей."""
        all_vacancies = []
        for emp_id in EMPLOYER_IDS:
            vacancies = self.get_vacancies_by_employer(emp_id)
            for vacancy in vacancies:
                all_vacancies.append(self.filter_vacancy(vacancy))
        return all_vacancies

    @staticmethod
    def filter_vacancy(vacancy):
        """Фильтрация вывода ваканский с данными"""
        if vacancy["salary"]:
            salary_from = vacancy["salary"]["from"] if vacancy["salary"]["from"] else 0
            salary_to = vacancy["salary"]["to"] if vacancy["salary"]["to"] else 0
        else:
            salary_from = 0
            salary_to = 0
        return {"id": vacancy["id"], "name": vacancy["name"], "area": vacancy["area"]["name"],
                "alternate_url": vacancy["alternate_url"], "salary_from": salary_from, "salary_to": salary_to}


def get_employer_vacancies(employer_id: str) -> list:
    """
    Получает список вакансий для работодателя.
    :param employer_id: ID работодателя на HH
    :return: список вакансий
    """
    url = "https://api.hh.ru/vacancies"  # Убраны пробелы
    params = {"employer_id": employer_id}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()["items"]
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return []
