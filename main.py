from src.config import load_config
from src.db_manager import DBManager
from src.hh_api import EMPLOYER_IDS, get_employer_vacancies
from src.utils import get_employer_info, save_vacancies_to_db, save_employers_to_db


config = load_config()

db_manager = DBManager(config)

employers = []


for emp_id in EMPLOYER_IDS:
    employer_data = get_employer_info(emp_id)
    employers.append(employer_data)
    vacancies = get_employer_vacancies(emp_id)
    save_vacancies_to_db(vacancies)

save_employers_to_db(employers)

print(db_manager.get_companies_and_vacancies_count())
print(db_manager.get_all_vacancies())
print(db_manager.get_avg_salary())
print(db_manager.get_vacancies_with_higher_salary())
print(db_manager.get_vacancies_with_keyword("Python"))
