### Состав проекта
Проект состоит из 2 сервисов -
БД (postgresql), бекенд (django).
Сервисы описаны в файлах docker-compose.yml и docker-compose.override.yml.
Последний необходим для локальных настроек и находится в .gitignore.

### Предварительная настройка
Перед первым запуском нужно создать docker-compose.override.yml в корне проекта.
Пример настройки development-окружения:
```docker/compose
version: '2.1'

services:
  backend:
    environment:
      # Пароль БД, обязательная настройка
      - POSTGRES_PASSWORD=%password%
      # Запуск django в debug-режиме
      - DEBUG=True
    ports:
      # Доступ к сервису с хоста
      - "8080:8080"
    volumes:
      # Возможность модифицировать код в контейнере
      - ./backend:/source

  db:
    environment:
      # Пароль БД, обязательная настройка
      - POSTGRES_PASSWORD=%password%
    volumes:
      # Постоянное хранение содержимого БД
      - ./db/pgdata:/var/lib/postgresql/data
    ports:
      # Доступ к БД с хоста
      - "5432:5432"
```

### Запуск локального инстанса
Пример запуска:
```
cd online_shop
docker-compose up -d
```
Запуска одного сервиса:
`docker-compose up -d %service%`
