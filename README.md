# Дипломный проект "Фудграм"

https://foodgrammm.myftp.org/

Этот проект представляет собой веб-приложение "Фудграм", где пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и использовать сервис "Список покупок" для создания списка продуктов, необходимых для приготовления блюд.

## Технологии

- Фронтенд: React
- Бэкенд: Django Rest Framework
- База данных: PostgreSQL
- Nginx
- Docker
- Gunicorn «Green Unicorn»
- Github actions

## Запуск проекта

Проект разделен на три контейнера: nginx, PostgreSQL и Django, запускаемые через docker-compose. Файлы для сборки фронтенда хранятся в репозитории foodgram-project-react в папке frontend.

Для запуска проекта выполните следующие шаги:
1. Склонируйте репозиторий foodgram-project-react на свой компьютер.
2. Создайте виртуальное окружение:
   - Windows
   ```bash
   python -m venv venv
   source venv/Scripts/activate
   ```
   - Linux/macOS
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Обновить PIP:
   - Windows
   ```bash
   python -m pip install --upgrade pip
   ```
   - Linux/macOS
   ```bash
   python3 -m pip install --upgrade pip
   ```
4. Установить зависимости из файла requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```
5. Создайте и заполните файл .env.
    ```bash
   SECRET_KEY
   DEBUG
   ALLOWED_HOSTS
   POSTGRES_USER
   POSTGRES_PASSWORD
   POSTGRES_DB
   DB_HOST
   DB_PORT
   ```
6. Запустите проект в трёх контейнерах с помощью Docker Compose:
   ```bash
    docker compose up
   ```
7. Сделайте миграцию:
   ```bash
    docker compose exec backend python manage.py migrate
   ```
8. Соберите статику:

    ```bash
    docker compose exec backend python manage.py collectstatic
    ```
    ```bash
    docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
    ```
9. Загрузите данные с ингредиентами:
   ```bash
    docker compose exec backend python manage.py import_ingredients
   ```
10. Если потребуется работа в панели администратора, создайте суперпользователя:
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```
## Прочее

Данные сохраняются в volumes для сохранения их состояния.
