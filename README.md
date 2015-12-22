
# Nextdoor Scheduler

![Apache](https://img.shields.io/hexpm/l/plug.svg) 
[![Build Status](https://travis-ci.org/Nextdoor/ndkale.svg?branch=master)](https://travis-ci.org/Nextdoor/ndkale)

``ndscheduler`` is a flexible python library for building your own cron-like system to schedule jobs, which is to run a tornado process to serve REST APIs and a web ui. It's like [LLVM](http://llvm.org/) that provides modular and reusable components for building a compiler. 

Check out our blog post - [We Don’t Run Cron Jobs at Nextdoor](https://engblog.nextdoor.com/2015/06/10/we-do-not-run-cron-jobs-at-nextdoor/)

## Table of contents
  
  * [Key Abstractions](#key-abstractions)
  * [How to Build a Cron-Replacement](#how-to-build-a-cron-replacement)
    * [Install ndscheduler](#install-ndscheduler)
    * [Run unit tests](#run-unit-tests)
    * [Clean everything and start from scratch](#clean-everything-and-start-from-scratch)
    * [Implement your own scheduler](#implement-your-own-scheduler)
    * [Reference Implementation](#reference-implementation)
  * [REST APIs](#rest-apis)
  * [Web UI](#web-ui)

## Key Abstractions

* [Core](https://github.com/Nextdoor/ndscheduler/tree/master/ndscheduler/core): a bunch of resuable components
  * [Datastore](https://github.com/Nextdoor/ndscheduler/tree/master/ndscheduler/core/datastore): manages database connections and makes queries; could support Postgres, MySQL, and sqlite.
    * Job: represents a schedule job and decides how to run a paricular job.
    * Execution: represents an instance of job execution.
    * AuditLog: logs when and who runs what job.
  * [ScheduleManager](https://github.com/Nextdoor/ndscheduler/blob/master/ndscheduler/core/scheduler_manager.py): Access Datastore to manage jobs, i.e., schedule/modify/delete/pause/resume a job.
* [Server](https://github.com/Nextdoor/ndscheduler/tree/master/ndscheduler/server): a tornado server that runs ScheduleManager and provides REST APIs and serves UI.
* [Web UI](https://github.com/Nextdoor/ndscheduler/tree/master/ndscheduler/static): a single page HTML app; this is a default implementation.

## How to Build a Cron-Replacement

### Install ndscheduler
From source code

    # Only need to run make init the first time you checkout the repo.
    # It sets up the python virtual environment in .venv directory.
    make init
    
    # Each time we introduce a new dependency in setup.py, you have to run this
    make install

### Run unit tests

    make test
    
### Clean everything and start from scratch
    
    make clean
    
### Implement your own scheduler

You have to implement three things for your scheduler, i.e., ``Settings``, ``Server``, and ``Jobs``.

**Settings**

In your implementation, you need to provide a settings file to override default settings (e.g., [settings in simple_scheduler](https://github.com/Nextdoor/ndscheduler/blob/master/simple_scheduler/settings.py)). You need to specify the python import path in the environment variable ``NDSCHEDULER_SETTINGS_MODULE`` before running the server.

All available settings can be found in [default_settings.py](https://github.com/Nextdoor/ndscheduler/blob/master/ndscheduler/default_settings.py) file.

**Server**

You need to have a server file to import and run ``ndscheduler.server.server.SchedulerServer``.

**Jobs**

Each job should be a standalone class that is a subclass of ``ndscheduler.job.JobBase`` and put the main logic of the job in ``run()`` function.

After you set up ``Settings``, ``Server`` and ``Jobs``, you can run the whole thing like this:

    NDSCHEDULER_SETTINGS_MODULE=simple_scheduler.settings \
    PYTHONPATH=.:$(PYTHONPATH) \
		    python simple_scheduler/scheduler.py

### Reference Implementation

See code in the [simple_scheduler/](https://github.com/Nextdoor/ndscheduler/tree/master/simple_scheduler) directory.

Run it

    make simple
    
Access the web ui via http://localhost:8888

## REST APIs

Please see [README.md in ndscheduler/server/handlers](https://github.com/Nextdoor/ndscheduler/blob/master/ndscheduler/server/handlers/README.md).

## Web UI

We provide a default implementation of web ui. You can replace the default web ui by overwriting these settings

    STATIC_DIR_PATH = :static asset directory paths:
    TEMPLATE_DIR_PATH = :template directory path:
    APP_INDEX_PAGE = :the file name of the single page app's html:
    
### The default web ui

**List of jobs**

![List of jobs](http://i.imgur.com/dGILbkZ.png)

**List of executions**

![List of executions](http://i.imgur.com/JpjzrlU.png)

**Audit Logs**

![Audit logs](http://i.imgur.com/eHLzHhw.png)

**Modify a job**

![Modify a job](http://i.imgur.com/uA26693.png)
