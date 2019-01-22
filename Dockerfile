FROM python:3.7.2
WORKDIR /usr/src/app/ndscheduler
COPY . ./
RUN make all
ENTRYPOINT [ "make", "simple" ]