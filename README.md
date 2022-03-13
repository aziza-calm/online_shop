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
      - POSTGRES_PASSWORD=%password%
      - DEBUG=True
    ports:
      - "8080:8080"
    volumes:
      - ./backend:/source

  db:
    environment:
      - POSTGRES_PASSWORD=%password%
    volumes:
      - ./db/pgdata:/var/lib/postgresql/data
    ports:
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
