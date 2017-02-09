from celery import Celery
import time

app = Celery('tasks', backend='redis://redis:6379/0', broker='redis://redis:6379/0')

@app.task
def add(x, y):
    return x + y

@app.task(ignore_result=False)
def sleep(s):
    time.sleep(s)
    return "Slept for {} seconds".format(s)


def buggy_function():
    raise Exception("Oops")

@app.task(ignore_result=False)
def buggy_task():
    time.sleep(10)
    return buggy_function()
