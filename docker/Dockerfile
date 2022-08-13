FROM debian:bullseye-slim

WORKDIR /web

COPY . .

RUN mv .env.example .env \
    && mkdir -p media logs static/COMPILED .well-known \
    && useradd -M -d /web -s /sbin/nologin uwsgi \
    && printf 'APT::Install-%s false;\n' \
        Recommends Suggests >/etc/apt/apt.conf.d/00minimal \
    && printf 'APT::Keep-Downloaded-Packages false;\n' \
        >>/etc/apt/apt.conf.d/00minimal \
    && apt-get update \
    && apt-get install -y \
        libjemalloc2 \
        python3-pip \
        python3-psycopg2 \
        uwsgi-plugin-python3 \
    && pip install --no-cache-dir -e .[csp,sentry] \
    && mv docker/uwsgi.ini /etc/uwsgi.ini \
    && rm -rf docker /var/lib/apt/lists/* \
    && ./manage.py collectstatic --no-input \
    && chown -R uwsgi:uwsgi /web

VOLUME /web/.well-known /web/media /web/logs

EXPOSE 3000 57475

STOPSIGNAL SIGINT

CMD ["uwsgi", "--ini", "/etc/uwsgi.ini"]
