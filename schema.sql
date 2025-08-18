
DROP TABLE IF EXISTS vacancies;
DROP TABLE IF EXISTS employers;


CREATE TABLE employers (
    employer_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    open_vacancies INTEGER
);

CREATE TABLE vacancies (
    vacancy_id SERIAL PRIMARY KEY,
    employer_id VARCHAR(20) REFERENCES employers(employer_id),
    name VARCHAR(255),
    salary_from INTEGER,
    salary_to INTEGER,
    currency VARCHAR(10),
    url TEXT
);