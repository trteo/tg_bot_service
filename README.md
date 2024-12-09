# bottec tg bot

### Env

Переменные окружения берутся из settings/env

Пример заполненных значений хранится в settings/env.example (все кроме Токена бота)


### Для запуска необходимо

* Создать бота
* Добавить в бота в канал и группу ТГ
* Добавить id и ссылки на канал и группу в settings/env
* Прописать конфиг поднятой БД в env (POSTGRES_HOST=gateway.docker.internal если Postgres поднят на устройстве)
* Заполнить БД (скрипт запускается при старте админки)
* Запустить


### Запуск докер контейнера
```commandline
docker build --progress=plain --no-cache -t bot . && \
docker run -it bot
```

