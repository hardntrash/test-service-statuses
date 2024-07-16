## Тестовое задание

Есть несколько рабочих сервисов, у каждого сервиса есть состояние работает/не работает/работает нестабильно.

Требуется написать API который:

1. Получает и сохраняет данные: имя, состояние, описание
2. Выводит список сервисов с актуальным состоянием
3. По имени сервиса выдает историю изменения состояния и все данные по каждому состоянию

Дополнительным плюсом будет

1. По указанному интервалу выдается информация о том сколько не работал сервис и считать SLA в процентах до 3-й запятой

Вывод всех данных должен быть в формате JSON


## Стэк:
* Python
* FastApi
* SqlAlchemy
* Alembic
* Poetry
* PostgreSQL

### .env
    # DB
    POSTGRES_SERVER=db # адресс
    POSTGRES_PORT=5432 # порт
    POSTGRES_DB=app # имя
    POSTGRES_USER=postgres # пользователь
    POSTGRES_PASSWORD=changethis # пароль

    # API
    APP_CONFIG__DB__URL="postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}:${POSTGRES_PORT}/${POSTGRES_DB}" # строка подключения к БД
    APP_CONFIG__DB__ECHO=False # отобржать или нет запросы SqlAlchemy

## Локальный запуск
### Установка зависимостей
    pip install poetry
    poetry install

### Запуск приложения
    /bin/bash service-statuses-app/start.sh

## Запуск в докере
    docker-compose up -d

