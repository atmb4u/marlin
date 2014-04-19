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
sudo apt-get install virtualenv
virtualenv marlin-env
source marlin-env/bin/activate
```

* requests, ujson, flask, python-daemon
```bash
pip install flask requests ujson python-daemon
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

