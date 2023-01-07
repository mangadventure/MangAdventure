FROM alpine:3.17

WORKDIR /web

COPY . .

RUN ([ -f .env ] || mv .env.example .env) \
    && mkdir -p .well-known logs media static/COMPILED \
    && touch static/styles/_variables.scss \
    && mv docker/uwsgi.ini /etc/uwsgi.ini \
    && apk add --no-cache \
        mimalloc2 \
        libsass \
        python3 \
        py3-pip \
        py3-psycopg2 \
        py3-redis \
        py3-wheel \
        uwsgi-python3 \
    && pip install --no-cache-dir \
        https://github.com/ObserverOfTime/libsass-python/releases/download/0.22.0%2Bmusl/libsass-0.22.0-cp37-abi3-musllinux_1_1_x86_64.whl \
    && pip install --no-cache-dir -e .[csp,sentry] \
    && ./manage.py collectstatic --no-input \
    && chown -R uwsgi:uwsgi /web \
    && apk del py3-pip py3-wheel \
    && rm -rf docker

VOLUME /web/logs \
       /web/media \
       /web/.well-known

EXPOSE 3000 57475

STOPSIGNAL SIGINT

CMD ["uwsgi", "--ini=/etc/uwsgi.ini", "--uid=uwsgi", "--gid=uwsgi"]
