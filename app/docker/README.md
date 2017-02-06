# Dockerize simple scheduler

## Build docker image
```bash
    docker build -t ndscheduler .
```

## Run a container

```bash
    docker run -it -p 8888:8888 \
	  -e "SIMPLE_SCHEDULER_SLACK_URL=$SLACK_API_URL" \
	  ndscheduler
```

You can now access the localhost:8888 for the web ui.
