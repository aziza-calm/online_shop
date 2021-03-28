FROM python:3.9-slim

COPY . /source
WORKDIR /source

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install -r requirements.txt

COPY docker/*.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/*.sh

EXPOSE 8000
ENTRYPOINT ["entrypoint.sh"]
