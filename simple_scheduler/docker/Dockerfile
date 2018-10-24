FROM python:3.6

# set vars
ENV LOCAL_APPDIR simple_scheduler
ENV WORK_APPDIR app
RUN mkdir -p /${WORK_APPDIR}

# install deps
WORKDIR /
RUN pip install --upgrade pip

# for local development only!
RUN mkdir -p /tmp/nds
COPY . /tmp/nds
RUN rm -rf /tmp/nds/simple_scheduler
RUN pip install --no-cache-dir -e /tmp/nds

ADD ${LOCAL_APPDIR}/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ${LOCAL_APPDIR} /${WORK_APPDIR}

WORKDIR /${WORK_APPDIR}
ENTRYPOINT ["/bin/bash", "docker/run_scheduler"]
