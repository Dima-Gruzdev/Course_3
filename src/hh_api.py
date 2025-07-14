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
    """"""
    def __init__(self):
        self.__url_employer = 'https://api.hh.ru/employers'
        self.__url_vacancies = 'https://api.hh.ru/vacancies'

    def get_employers(self):
        params = {"sort_by": "by_vacancies_open", "per_page": 10}
        try:
            response = requests.get(self.__url_employer, params=params)
            response.raise_for_status()
            employers = response.json().get("items", [])
            return [{"id": employer["id"], "name": employer["name"]} for employer in employers]
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
            return []

    def get_vacancies_by_employer(self, employer_id):
        params = {"employer_id": employer_id, "per_page": 50}
        response = requests.get(self.__url_vacancies, params=params).json()["items"]
        return response

    def get_all_vacancies_by_employers(self):
        employers = self.get_employers()
        all_vacancies = []
        for employer in employers:
            vacancies = self.get_vacancies_by_employer(employer["id"])
            all_vacancies.extend([self.filter_vacancy(vacancy) for vacancy in vacancies])
        return all_vacancies

    @staticmethod
    def filter_vacancy(vacancy):
        if vacancy["salary"]:
            salary_from = vacancy["salary"]["from"] if vacancy["salary"]["from"] else 0
            salary_to = vacancy["salary"]["to"] if vacancy["salary"]["to"] else 0
        else:
            salary_from = 0
            salary_to = 0
        return {"id": vacancy["id"], "name": vacancy["name"], "area": vacancy["area"]["name"],
                "alternate_url": vacancy["alternate_url"], "salary_from": salary_from, "salary_to": salary_to}


hh = HHParser()
print(hh.get_all_vacancies_by_employers())


def get_employer_vacancies(employer_id: str) -> list:
    """
    Получает список вакансий для работодателя.
    :param employer_id: ID работодателя на HH
    :return: список вакансий
    """
    url = "https://api.hh.ru/vacancies"
    params = {"employer_id": employer_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["items"]
