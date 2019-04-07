FROM python:3.7.3-alpine AS ndscheduler_setup
WORKDIR /usr/src/app/ndscheduler
ENV PYTHONPATH "${PYTHONPATH}:."
COPY ./requirements.txt ./
COPY ./simple_scheduler/requirements.txt ./simple_scheduler/
COPY package.json ./
RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install -r requirements.txt && \
    pip install -r simple_scheduler/requirements.txt && \
    apk --purge del .build-deps && \
    apk update && apk add nodejs-npm && npm install