FROM python:3.7.2 AS ndscheduler_setup
WORKDIR /usr/src/app/ndscheduler
ENV PYTHONPATH "${PYTHONPATH}:."
COPY ./requirements.txt ./
COPY ./simple_scheduler/requirements.txt ./simple_scheduler/
RUN ["pip", "install", "-r", "requirements.txt"]
RUN ["pip", "install", "-r", "simple_scheduler/requirements.txt"]
COPY install-npm.sh ./
COPY package.json ./
RUN chmod +x install-npm.sh
RUN ./install-npm.sh
RUN npm install