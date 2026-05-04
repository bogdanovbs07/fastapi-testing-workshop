@echo off

REM Установка зависимостей
pip install -r requirements.txt

REM Запуск тестов с генерацией результатов Allure
pytest tests/ -v --alluredir=allure-results --clean-alluredir

REM Генерация отчета Allure
allure generate allure-results -o allure-report --clean

REM Открытие отчета в браузере
allure open allure-report

echo Allure отчет сгенерирован и открыт в браузере
