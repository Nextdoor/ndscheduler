FROM ubuntu:14.04

MAINTAINER Wenbin Fang <wenbin@nextdoor.com>

RUN apt-get -qq update && \
    apt-get -qq install python-virtualenv git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN virtualenv /mnt/scheduler && \
    . /mnt/scheduler/bin/activate && \
    pip install -e git+https://github.com/Nextdoor/ndscheduler.git#egg=ndscheduler && \
    pip install -r /mnt/scheduler/src/ndscheduler/simple_scheduler/requirements.txt && ls

ADD run_scheduler /mnt/scheduler/bin/run_scheduler
RUN chmod 755 /mnt/scheduler/bin/run_scheduler

CMD ["/mnt/scheduler/bin/run_scheduler"]
