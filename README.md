API для управления заметками

Эндпоинты для работы с ресурсами

    Регистрация и аутентификация, управление правами
    - POST /users/sign-up регистрация пользователя (в качестве username используется email)
    - POST /users/token получение аутентификационного токен
    - PATCH /users/update-role предоставление/лишение прав      администратора

    Работа с заметками (доступно только авторизованным пользователя)
    - POST /notes/create создание заметки
    - GET /notes/my-notes получение пользователем списка его заметок
    - GET /notes/{note_uuid} получение конкретной заетки пользователя
    - PATCH /notes/update_note обновление заметки
    - DELETE /notes/{note_uuid} удаление заметки

    Работа с заметками доступная только пользователя с ролью Admin и Superuser
    - DELETE /notes/staff/restore_note/{note_uuid} восстановление удаленной заметки
    - GET /notes/staff/get_note/{note_uuid} получение любой заметки
    - GET /notes/staff/get_notes получение всех заметок в системе
    - GET /notes/staff/get_notes_users/{username} получение списка заметок конкретного пользователя

#### Стек технологий:
    - Python3.11
    - MongoDB - СУБД
    - FastAPI - API
    - Docker

#### Запуск приложения

- Копируем код приложения в Вашу директорию.

``

- Запускаем контейнеры

`docker compose up -d`

- Создаем суперпользователя при необходимости:
    login: admin@examle.com
    password: admin

`docker exec app python init_superuser.py`

Приложение готово для тестирования:

http://127.0.0.1:8000/docs

#### Запуск тестов

`docker exec app python -m unittest`