FROM python:3.7.3-alpine AS ndscheduler_common
WORKDIR /usr/src/app/ndscheduler
ENV PYTHONPATH "${PYTHONPATH}:."
COPY ./requirements.txt ./
COPY ./simple_scheduler/requirements.txt ./simple_scheduler/
RUN apk update && apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install -r requirements.txt && \
    pip install -r simple_scheduler/requirements.txt && \
    apk --purge del .build-deps

FROM ndscheduler_common AS ndscheduler_dev
COPY package.json ./
RUN apk add nodejs-npm && npm install