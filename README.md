### Project components
There are 2 services:
DB (postgresql) and backend (Django).
Services are described in docker-compose.yml file.

### Docker-compose example
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

### Run
Run example:
```
cd online_shop
docker-compose up -d
```
Run one service:
```
docker-compose up -d %service%
```
Run tests:
```
docker exec -it osh_backend bash
```
and then:
```
python3 manage.py test
```
