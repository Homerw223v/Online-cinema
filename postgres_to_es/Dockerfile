FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /postgres_to_es
# Ограничение доступа к папке с кодовой базой
RUN groupadd -r developers && useradd -d /postgres_to_es -r -g developers developer \
    && chown developer:developers -R /postgres_to_es
COPY requirements.txt /postgres_to_es

RUN pip install --no-cache-dir -r requirements.txt
COPY . /postgres_to_es

# make wait-for-postgres.sh executable
RUN chmod +x wait-for-postgres.sh