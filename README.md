![Marlin](https://github.com/atmb4u/marlin/blob/master/marlin/static/marlin.jpg?raw=true)

Marlin
======

#### a fast, frill-free REST API with ZERO setup time is too interesting.

Quick Start Guide
-----------------

```bash

pip install marlin  # install marlin to the python environment.

marlin-server start  # start marlin server - port: 5000

```


Detailed Installation in Ubuntu
-------------------------------

* redis-server

```bash
sudo apt-get install redis-server
```
* create virtualenv

```bash
sudo apt-get install python-pip
sudo pip install virtualenv
virtualenv marlin-env
source marlin-env/bin/activate
```

* requests, ujson, flask, python-daemon
```bash
pip install flask requests ujson python-daemon redis
```

* install marlin

```bash
pip install marlin  # install marlin to the python environment.

```


Managing Server
---------------

```bash
marlin-server start  # starts server with default conf on port 5000

marlin-server stop  # stops the server

marlin-server restart  # restart the server

marlin-server live  # starts a server on DEBUG mode
```

Request Methods
---------------


| METHOD        | URL                               | RESPONSE    |              DESCRIPTION                |
| ------------- |:--------------------------------: | :----------:| :--------------------------------------:|
| GET           | /api/v1/<model>/?start=1&end=10   |[data] 1-10  | returns the 1-10 elements in the <model>|
| GET           | /api/v1/<model>/1                 |  data item  |  returns the element with id 1          |
| GET           | /ping/                            |  200/500    |   check if service is up and connected  |
| POST          | /api/v1/<model>/                  |    [data]   |        adds data to the model           |
| PUT           | /api/v1/<model>/1/                |    [data]   |             edit data                   |
| DELETE        | /api/v1/<model>/1                 |    200      |         delete the data item            |
| DELETE        | /api/v1/<model>/                  |     -       |         delete complete data in model   |
| DELETE        | /api/v1/<model>/&force=1          |     -       | delete and reset model (starts with id=1|


Server Configuration
--------------------

__marlin.config__

For custom configuration, just create a __marlin.config__ on the directory from where you are starting marlin-server.

```

[SERVER]
DEBUG = True
PID_FILE = /tmp/marlin.pid
LOG_FILE = /tmp/marlin.log
SERVER_PORT = 5000

[REDIS]
REDIS_SERVER = localhost
REDIS_PORT = 6379
API_PREFIX = /api/

[APP]
APP_NAME = marlin
```

Custom urls and functions
----------------

Always, a basic REST API is just a scaffolding for the application, and custom defined urls and functions make it beautiful. As marlin is more focused on performance, it is designed for flexibility as well.

It is pretty simple to create custom functions in Marlin.

Just place ```marlin_function.py``` in the present working directory (pwd), with custom routes and custom responses.


```python
# marlin_functions.py
from marlin import app


@app.route("/example/"):
    return Response("Simple Custom Response")
```

or a more complex example.

### To get a custom element based on a user id

```python
import json
from marlin import app, RedisDatabaseManager
from flask import Response, request


@app.route("/simple_get/<model>")
def custom_get(model):
    rdm = RedisDatabaseManager(request, model, version='v1')
    user_id = 127
    if rdm:
        rdm.manipulate_data()
        rdm.get_from_redis(user_id)  # get data for the specific user id
    else:
        return json.dumps({"status": "Something is not right"})
    if rdm.status and rdm.data:
        return Response(rdm.string_data, content_type='application/json; charset=utf-8')
    elif rdm.status:
        return Response(json.dumps({'status': "No data Found"}), content_type='application/json; charset=utf-8',
                        status=404)
    else:
        return json.dumps({"status": "Something is not right"})
```


A little more complicated Example
### Following example filter all the objects with ```name=Apple```

```python
@app.route('/<model>/', methods=['GET'])
def little_complicated(model):
    custom_range_start = 10
    custom_range_end = 70
    error_response = Response(json.dumps(
        {'status': "Some unknown error"}),
        content_type='application/json; charset=utf-8', status=500)
    rdm = RedisDatabaseManager(request, model=model)
    if rdm:
        rdm.manipulate_data()
        rdm.get_many_from_redis(custom_range_start, custom_range_end)
    else:
        return error_response
    if rdm.status:
        if rdm.data:
            custom_query_set = []
            for datum in rdm.data:
                if datum.get("name") == "Apple":
                    custom_query_set.append(datum)
            return Response(json.dumps(custom_query_set), content_type='application/json; charset=utf-8')
        else:
            return Response(json.dumps({'status': "No data Found"}), content_type='application/json; charset=utf-8',
                            status=404)
    else:
        return error_response
```
