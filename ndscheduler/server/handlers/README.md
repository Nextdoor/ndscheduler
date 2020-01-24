# REST APIs

  * [Run it NOW](#run-it-now)
  * [REST APIs](#rest-apis)
    * [Jobs](#jobs)
      * [Get all jobs](#get-all-jobs)
      * [Get a job](#get-a-job)
      * [Create a new job](#create-a-new-job)
      * [Delete a job](#delete-a-job)
      * [Modify a job](#modify-a-job)
      * [Pause a job](#pause-a-job)
      * [Resume a job](#resume-a-job)
    * [Executions](#executions)
      * [Get executions within time range](#get-executions-within-time-range)
      * [Get an execution](#get-an-execution)
      * [Run a job](#run-a-job)
    * [Audit logs](#audit-logs)
      * [Get logs within time range](#get-logs-within-time-range)

## Run it NOW
```bash
    # Start server
    $ git clone https://github.com/Nextdoor/ndscheduler.git
    $ cd ndscheduler
    $ make simple
   
    # Add a job
    $ curl -X POST localhost:8888/api/v1/jobs \
       --header "Content-Type:application/json" \
       -d "{\"job_class_string\": \"simple_scheduler.jobs.sample_job.AwesomeJob\", \
            \"name\": \"My first job\", \"pub_args\": [\"arg1\", 2], \
            \"trigger\": \"cron\", \"trigger_params\": {\"minute\": \"*/1\"}}"
   
    # Get all jobs
    $ curl localhost:8888/api/v1/jobs
```

## REST APIs      
### Jobs

#### Difference between a Cron job and an Interval job

Version 2 of the API supports next to the already existing Cron jobs also
Interval jobs. Therefore the API of the jobs has to be changed. A job uses the
string parameter ```trigger``` that indicates the job type. Possible values are
 ```cron``` or ```interval```. The parameters for the chosen job type can be set
by the ```trigger_params```.   

* **Cron Job**

  A cron job is defined by the ```trigger``` = ```cron```. A cron
  job needs the parameters ```month```, ```day_of_week```, ```day```,
  ```hour```, ```minute``` parameters within the ```trigger_params```.

      {
      "job_id": "d8f376e858a411e4b6ae22000ac58d05",
      "job_class_string": "simple_scheduler.jobs.clean_apns.CleanAPNsJob",
      "name": "Clean APNs",
      "pub_args": ["arg1": 1, "arg2": 2],
      "trigger": "cron",
      "trigger_params": {
        "month": "*",
        "day_of_week": "*",
        "day": "*",
        "hour": "*/1",
        "minute": "*"}


* **Interval Job**

  An interval job is defined by the ```trigger``` = ```interval```. An interval
  job needs the ```interval``` parameter within the ```trigger_params```. The
  interval is defined in seconds.

      {
      "job_id": "d8f376e858a411e4b6ae22000ac58d05",
      "job_class_string": "simple_scheduler.jobs.clean_apns.CleanAPNsJob",
      "name": "Clean APNs",
      "pub_args": ["arg1": 1, "arg2": 2],
      "trigger": "interval",
      "trigger_params": {
        "interval": 3600}


#### Get all jobs

  Returns json data for all jobs.

* **URL**

  /api/v1/jobs

* **Method:**

  `GET`
  
*  **URL Params**

   None

* **Data Params**

   None

* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:** 

        {
            jobs: [{
                "job_id": "d8f376e858a411e4b6ae22000ac58d05",
                "job_class_string": "simple_scheduler.jobs.clean_apns.CleanAPNsJob",
                "name": "Clean APNs",
                "pub_args": ["arg1": 1, "arg2": 2],
                "trigger": "cron",
                "trigger_params": {
                  "month": "*",
                  "day_of_week": "*",
                  "day": "*",
                  "hour": "*/1",
                  "minute": "*"}
            },
            ...]
        }

* **Error Response:**

  * **Code:** 400 Bad Request <br />
    **Content:** 
    
        `{ error: "incorrect parameters" }`

  OR

  * **Code:** 500 Internal Server Error <br />
    **Content:** 
    
        `{ error: "server side error" }`

* **Sample Call:**

  ```javascript
    $.ajax({
      url: "/api/v1/jobs",
      dataType: "json",
      type : "GET",
      success : function(r) {
        console.log(r);
      }
    });
  ```

#### Get a job

  Returns json data for a job.

* **URL**

  /api/v1/jobs/:job_id:

* **Method:**

  `GET`
  
*  **URL Params**

   None

* **Data Params**

   None

* **Success Response:**

  * **Return for a Cron job**  
    **Code:** 200 OK <br />
    **Content:** 

        {
          "job_id": "d8f376e858a411e4b6ae22000ac58d05",
          "job_class_string": "simple_scheduler.jobs.clean_apns.CleanAPNsJob",
          "name": "Clean APNs",
          "pub_args": ["arg1": 1, "arg2": 2],
          "trigger": "cron",
          "trigger_params": {
            "month": "*",
            "day_of_week": "*",
            "day": "*",
            "hour": "*/1",
            "minute": "*"}
        }

  * **Return for an Interval job**  
    **Code:** 200 OK <br />
    **Content:** 

        {
          "job_id": "d8f376e858a411e4b6ae22000ac58d05",
          "job_class_string": "simple_scheduler.jobs.clean_apns.CleanAPNsJob",
          "name": "Clean APNs",
          "pub_args": ["arg1": 1, "arg2": 2],
          "trigger": "interval",
          "trigger_params": {
            "interval": 3600}
        }

    
* **Error Response:**

  * **Code:** 400 Bad Request <br />
    **Content:** 
    
        `{ error: "incorrect parameters" }`

  OR

  * **Code:** 500 Internal Server Error <br />
    **Content:** 
    
        `{ error: "server side error" }`

* **Sample Call:**

  ```javascript
    $.ajax({
      url: "/api/v1/jobs/ad9bb256a2ee11e5bbf702ba903740c3",
      dataType: "json",
      type : "GET",
      success : function(r) {
        console.log(r);
      }
    });
  ```
  
#### Create a new job

  Create a new job and return the job id.

* **URL**

  /api/v1/jobs

* **Method:**

  `POST`
  
*  **URL Params**

   None

* **Data Params for a Cron job**

        {
            "job_class_string": "simple_scheduler.jobs.clean_apns.CleanAPNsJob",
            "name": "Clean APNs",
            "pub_args": ["arg1": 1, "arg2": 2],
            "trigger": "cron",
            "trigger_params": {
              "month": "*",
              "day_of_week": "*",
              "day": "*",
              "hour": "*/1",
              "minute": "*"}
        }

* **Data Params for an Interval job**

        {
            "job_class_string": "simple_scheduler.jobs.clean_apns.CleanAPNsJob",
            "name": "Clean APNs",
            "pub_args": ["arg1": 1, "arg2": 2],
            "trigger": "interval",
            "trigger_params": {
              "interval": 3600}
        }


Required fields: `job_class_string` and `name`

* **Success Response:**

  * **Code:** 201 Created <br />
    **Content:** `{ job_id: "d8f376e858a411e4b6ae32000ac58d05"}`
 
* **Error Response:**

  * **Code:** 400 Bad Request <br />
    **Content:** `{ error: "incorrect parameters" }`

  OR

  * **Code:** 500 Internal Server Error <br />
    **Content:** `{ error: "server side error" }`

* **Sample Call:**

  ```javascript
    $.ajax({
      url: "/api/v1/jobs",
      dataType: "json",
      contentType: "application/json",
      type : "POST",
      data: {
            "job_class_string": "simple_scheduler.jobs.clean_apns.CleanAPNsJob",
            "name": "Clean APNs",
            "pub_args": ["arg1": 1, "arg2": 2],
            "trigger": "interval",
            "trigger_params": {
              "interval": 3600}
      },
      success : function(r) {
        console.log(r);
      }
    });
  ```
    
#### Delete a job

  Delete a job and returns json data for old job id.

* **URL**

  /api/v1/jobs/:job_id:

* **Method:**

  `DELETE`
  
*  **URL Params**

   None

* **Data Params**

   None

* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:** 

        {
          "job_id": "d8f376e858a411e4b6ae22000ac58d05"
        }
    
* **Error Response:**

  * **Code:** 400 Bad Request <br />
    **Content:** 
    
        `{ error: "incorrect parameters" }`

  OR

  * **Code:** 500 Internal Server Error <br />
    **Content:** 
    
        `{ error: "server side error" }`

* **Sample Call:**

  ```javascript
    $.ajax({
      url: "/api/v1/jobs/d8f376e858a411e4b6ae22000ac58d05",
      dataType: "json",
      type : "DELETE",
      success : function(r) {
        console.log(r);
      }
    });
  ```
    
#### Modify a job
    
  Modify a job and returns json data for job id.

* **URL**

  /api/v1/jobs/:job_id:

* **Method:**

  `PUT`
  
*  **URL Params**

   None

* **Data Params for a Cron job**

        {
            "job_class_string": "simple_scheduler.jobs.clean_apns.CleanAPNsJob",
            "name": "Clean APNs",
            "pub_args": ["arg1": 1, "arg2": 2],
            "trigger": "cron",
            "trigger_params": {
              "month": "*",
              "day_of_week": "*",
              "day": "*",
              "hour": "*/1",
              "minute": "*"}
        }


* **Data Params for an Interval job**

        {
            "job_class_string": "simple_scheduler.jobs.clean_apns.CleanAPNsJob",
            "name": "Clean APNs",
            "pub_args": ["arg1": 1, "arg2": 2],
            "trigger": "interval",
            "trigger_params": {
              "interval": 3600}
        }

* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:** 

        {
          "job_id": "d8f376e858a411e4b6ae22000ac58d05"
        }
    
* **Error Response:**

  * **Code:** 400 Bad Request <br />
    **Content:** 
    
        `{ error: "incorrect parameters" }`

  OR

  * **Code:** 500 Internal Server Error <br />
    **Content:** 
    
        `{ error: "server side error" }`

* **Sample Call:**

  ```javascript
    $.ajax({
      url: "/api/v1/jobs/d8f376e858a411e4b6ae22000ac58d05",
      dataType: "json",
      type : "PUT",
      data: {
        "job_class_string": "simple_scheduler.jobs.clean_apns.CleanAPNsJob",
        "name": "Clean APNs",
        "pub_args": ["arg1": 1, "arg2": 2],
        "trigger": "interval",
        "trigger_params": {
          "interval": 3600}
      },
      success : function(r) {
        console.log(r);
      }
    });
  ```
    
#### Pause a job

  Pause a job and returns json data for job id.

* **URL**

  /api/v1/jobs/:job_id:

* **Method:**

  `PATCH`
  
*  **URL Params**

   None

* **Data Params**

   None

* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:** 

        {
          "job_id": "d8f376e858a411e4b6ae22000ac58d05",
        }
    
* **Error Response:**

  * **Code:** 400 Bad Request <br />
    **Content:** 
    
        `{ error: "incorrect parameters" }`

  OR

  * **Code:** 500 Internal Server Error <br />
    **Content:** 
    
        `{ error: "server side error" }`

* **Sample Call:**

  ```javascript
    $.ajax({
      url: "/api/v1/jobs/d8f376e858a411e4b6ae22000ac58d05",
      dataType: "json",
      type : "PATCH",
      success : function(r) {
        console.log(r);
      }
    });
  ```
    
#### Resume a job

  Resume a paused job and returns json data for job id.

* **URL**

  /api/v1/jobs/:job_id:

* **Method:**

  `OPTIONS`
  
*  **URL Params**

   None

* **Data Params**

   None

* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:** 

        {
          "job_id": "d8f376e858a411e4b6ae22000ac58d05",
        }
    
* **Error Response:**

  * **Code:** 400 Bad Request <br />
    **Content:** 
    
        `{ error: "incorrect parameters" }`

  OR

  * **Code:** 500 Internal Server Error <br />
    **Content:** 
    
        `{ error: "server side error" }`

* **Sample Call:**

  ```javascript
    $.ajax({
      url: "/api/v1/jobs/d8f376e858a411e4b6ae22000ac58d05",
      dataType: "json",
      type : "OPTIONS",
      success : function(r) {
        console.log(r);
      }
    });
  ```

### Executions

#### Get executions within time range
 
  Returns json data for all executions within given time range.

* **URL**

  /api/v1/executions

* **Method:**

  `GET`
  
*  **URL Params**

   time_range_start=2015-12-19T00:31:50.313Z
   time_range_end=2015-12-19T01:31:50.313Z

* **Data Params**

   None

* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:** 

        {
            executions: [{
                description: "",
                execution_id: "7252d7a6a80f11e58bcc02ba903740c3",
                hostname: "",
                job: {
                    job_id: "bb0dec52797f11e4a14122000a150f89",
                    trigger: "cron",
                    trigger_params: {
                      day: "*",
                      day_of_week: "*",
                      hour: "*",
                      minute: "*/5",
                      month: "*"},
                    name: "Poll sendgrid for bounces and spamreports",
                    pub_args: [],
                    job_class_string: "simple_scheduler.jobs.sample_job.ImportDataJob",
                    week: "*"
                },
                pid: -1,
                scheduled_time: "2015-12-21T18:20:05.604708+00:00",
                state: "scheduled",
                task_id: "",
                updated_time: "2015-12-21T18:20:05.604732+00:00"
            },
            ...]
        }
    
* **Error Response:**

  * **Code:** 400 Bad Request <br />
    **Content:** 
    
        `{ error: "incorrect parameters" }`

  OR

  * **Code:** 500 Internal Server Error <br />
    **Content:** 
    
        `{ error: "server side error" }`

* **Sample Call:**

  ```javascript
    $.ajax({
      url: "/api/v1/executions?time_range_end=2015-12-19T01:31:50.313Z&time_range_start=2015-12-19T00:31:50.313Z",
      dataType: "json",
      type : "GET",
      success : function(r) {
        console.log(r);
      }
    });
  ```
    
#### Get an execution

  Returns json data for an execution.

* **URL**

  /api/v1/executions/:execution_id:

* **Method:**

  `GET`
  
*  **URL Params**

   None

* **Data Params**

   None

* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:** 

        {
            description: "",
            execution_id: "7252d7a6a80f11e58bcc02ba903740c3",
            hostname: "",
            job: {
                job_id: "bb0dec52797f11e4a14122000a150f89",
                trigger: "cron",
                    trigger_params: {
                      day: "*",
                      day_of_week: "*",
                      hour: "*",
                      minute: "*/5",
                      month: "*"},
                name: "Poll sendgrid for bounces and spamreports",
                pub_args: [],
                job_class_string: "simple_scheduler.jobs.sample_job.ImportDataJob",
                week: "*"
            },
            pid: -1,
            scheduled_time: "2015-12-21T18:20:05.604708+00:00",
            state: "scheduled",
            task_id: "",
            updated_time: "2015-12-21T18:20:05.604732+00:00"
        }
    
* **Error Response:**

  * **Code:** 400 Bad Request <br />
    **Content:** 
    
        `{ error: "incorrect parameters" }`

  OR

  * **Code:** 500 Internal Server Error <br />
    **Content:** 
    
        `{ error: "server side error" }`

* **Sample Call:**

  ```javascript
    $.ajax({
      url: "/api/v1/executions/d8f376e858a411e4b6ae22000ac58d05",
      dataType: "json",
      type : "GET",
      success : function(r) {
        console.log(r);
      }
    });
  ```
    
#### Run a job

  Run a job (create an execution) and returns json data for execution id.

* **URL**

  /api/v1/executions

* **Method:**

  `POST`
  
*  **URL Params**

   None

* **Data Params**

   None

* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:** { execution_id: "d8f376e858a411e4b6ae32000ac58d05" }
    
* **Error Response:**

  * **Code:** 400 Bad Request <br />
    **Content:** 
    
        `{ error: "incorrect parameters" }`

  OR

  * **Code:** 500 Internal Server Error <br />
    **Content:** 
    
        `{ error: "server side error" }`

* **Sample Call:**

  ```javascript
    $.ajax({
      url: "/api/v1/executions",
      dataType: "json",
      type : "POST",
      success : function(r) {
        console.log(r);
      }
    });
  ```

### Audit Logs

#### Get logs within time range

  Returns json data for audit logs within given time range.

* **URL**

  /api/v1/logs

* **Method:**

  `GET`
  
*  **URL Params**

   time_range_start=2015-12-19T00:31:50.313Z
   time_range_end=2015-12-19T01:31:50.313Z

* **Data Params**

   None

* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:** 

        {
            logs: [{
                    created_time: "2015-12-19T01:20:23.843895+00:00"
                    description: "ad9bb256a2ee11e5bbf702ba903740c3"
                    event: "custom_run"
                    job_id: "5052939245f611e5bef70610a8516d8b"
                    job_name: "Import Data Job"
                    user: "wenbin"
            },
            ...]
        }
    
* **Error Response:**

  * **Code:** 400 Bad Request <br />
    **Content:** 
    
        `{ error: "incorrect parameters" }`

  OR

  * **Code:** 500 Internal Server Error <br />
    **Content:** 
    
        `{ error: "server side error" }`

* **Sample Call:**

  ```javascript
    $.ajax({
      url: "/api/v1/logs?time_range_end=2015-12-19T01:31:50.313Z&time_range_start=2015-12-19T00:31:50.313Z",
      dataType: "json",
      type : "GET",
      success : function(r) {
        console.log(r);
      }
    });
  ```
