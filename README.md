# Foodgram2 (FastAPI, PostgreSQL, raw SQL)

## Запуск в Docker
1. Убедитесь, что Docker и docker-compose установлены.
2. Создайте файл `.env` в корне (рядом с `docker-compose.yml`)
3. Поднимите сервисы:
   ```
   docker-compose up --build -d
   ```
4. API будет доступно на `http://localhost:8000`, документация — `http://localhost:8000/docs`. Adminer для работы с БД — `http://localhost:8080` (сервер `db`, логин/пароль `foodgram`).

## Загрузка медиа
Файлы хранятся в `./media` (проброшен в контейнер). Для картинок используйте base64-строку в полях `image`/`avatar` или готовый URL `/media/...`.

## Зависимости
Установлены в `requirements.txt`; для локального запуска без Docker можно выполнить:
```
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Не забудьте поднять Postgres и выставить `DATABASE_URL`.

**Выполнил:** Беляев Вадим
