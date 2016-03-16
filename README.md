# Nextdoor Scheduler

![Apache](https://img.shields.io/hexpm/l/plug.svg) 
[![Build Status](https://travis-ci.org/Nextdoor/ndscheduler.svg)](https://travis-ci.org/Nextdoor/ndscheduler)
![GitHub Release](https://img.shields.io/github/release/Nextdoor/ndscheduler.svg)

``ndscheduler`` is a flexible python library for building your own cron-like system to schedule jobs, which is to run a tornado process to serve REST APIs and a web ui. It's like [LLVM](http://llvm.org/) that provides modular and reusable components for building a compiler. 

Check out our blog post - [We Don’t Run Cron Jobs at Nextdoor](https://engblog.nextdoor.com/we-don-t-run-cron-jobs-at-nextdoor-6f7f9cc62040#.d2erw1pl6)

**``ndscheduler`` currently supports Python 2 & 3 on Mac OS X / Linux.**

## Table of contents
  
  * [Key Abstractions](#key-abstractions)
  * [Try it NOW](#try-it-now)
  * [How to build Your own cron-replacement](#how-to-build-your-own-cron-replacement)
    * [Install ndscheduler](#install-ndscheduler)
    * [Three things](#three-things)
    * [Reference Implementation](#reference-implementation)   
  * [Contribute code to ndscheduler](#contribute-code-to-ndscheduler)
  * [REST APIs](#rest-apis)
  * [Web UI](#web-ui)

## Key Abstractions

* [Core](https://github.com/Nextdoor/ndscheduler/tree/master/ndscheduler/core): a bunch of resuable components
  * [Datastore](https://github.com/Nextdoor/ndscheduler/tree/master/ndscheduler/core/datastore): manages database connections and makes queries; could support Postgres, MySQL, and sqlite.
    * Job: represents a schedule job and decides how to run a paricular job.
    * Execution: represents an instance of job execution.
    * AuditLog: logs when and who runs what job.
  * [ScheduleManager](https://github.com/Nextdoor/ndscheduler/blob/master/ndscheduler/core/scheduler_manager.py): access Datastore to manage jobs, i.e., schedule/modify/delete/pause/resume a job.
* [Server](https://github.com/Nextdoor/ndscheduler/tree/master/ndscheduler/server): a tornado server that runs ScheduleManager and provides REST APIs and serves UI.
* [Web UI](https://github.com/Nextdoor/ndscheduler/tree/master/ndscheduler/static): a single page HTML app; this is a default implementation.

## Try it NOW

From source code:

    git clone https://github.com/Nextdoor/ndscheduler.git
    cd ndscheduler
    make simple

Or use docker:

    docker run -it -p 8888:8888 wenbinf/ndscheduler
    
Open your browser and go to [localhost:8888](http://localhost:8888). 

**Demo**
(Click for fullscreen play)
![ndscheduler demo](https://giant.gfycat.com/NastyBossyBeaver.gif)

## How to build Your own cron-replacement

### Install ndscheduler
Using pip (from GitHub repo)

    #
    # Put this in requirements.txt, then run
    #    pip install -r requirements.txt
    #

    # If you want the latest build
    git+https://github.com/Nextdoor/ndscheduler.git#egg=ndscheduler

    # Or put this if you want a specific commit
    git+https://github.com/Nextdoor/ndscheduler.git@5843322ebb440d324ca5a66ba55fea1fd00dabe8

    # Or put this if you want a specific tag version
    git+https://github.com/Nextdoor/ndscheduler.git@v0.1.0#egg=ndscheduler
    
    #
    # Run from command line
    #

    pip install -e git+https://github.com/Nextdoor/ndscheduler.git#egg=ndscheduler

(We'll upload the package to PyPI soon.)

### Three things

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

See code in the [simple_scheduler/](https://github.com/Nextdoor/ndscheduler/tree/master/simple_scheduler) directory for inspiration :)

Run it

    make simple
    
Access the web ui via [localhost:8888](http://localhost:8888)

The reference implementation also comes with [several sample jobs](https://github.com/Nextdoor/ndscheduler/tree/master/simple_scheduler/jobs).
* AwesomeJob: it just prints out 2 arguments you pass in.
* SlackJob: it sends a slack message periodically, for example, team standup reminder.
* ShellJob: it runs an executable command, for example, run curl to crawl web pages.
* CurlJob: it's like running [curl](http://curl.haxx.se/) periodically.

And it's [dockerized](https://github.com/Nextdoor/ndscheduler/tree/master/simple_scheduler/docker).

## Contribute code to ndscheduler

**Install dependencies**

    # Each time we introduce a new dependency in setup.py, you have to run this
    make install

**Run unit tests**

    make test
    
**Clean everything and start from scratch**
    
    make clean

Finally, send pull request. Please make sure the [CI](https://travis-ci.org/Nextdoor/ndscheduler) passes for your PR.

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

![Modify a job](http://i.imgur.com/aWv6xOR.png)
