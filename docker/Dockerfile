FROM alpine:edge

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
        py3-psycopg2 \
        py3-redis \
        uwsgi-python3 \
        -X https://dl-cdn.alpinelinux.org/alpine/edge/testing/ \
    && apk add --no-cache -t .build-deps \
        build-base \
        libsass-dev \
        py3-pip \
        py3-wheel \
        python3-dev \
    && export SYSTEM_SASS=1 \
    && pip install --no-cache-dir -e .[csp,sentry] \
    && ./manage.py collectstatic --no-input \
    && chown -R uwsgi:uwsgi /web \
    && apk del .build-deps \
    && rm -rf docker

VOLUME /web/logs \
       /web/media \
       /web/.well-known

EXPOSE 3000 57475

STOPSIGNAL SIGINT

CMD ["uwsgi", "--ini=/etc/uwsgi.ini", "--uid=uwsgi", "--gid=uwsgi"]
