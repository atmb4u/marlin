Marlin
======

### Easy Rest API to bootstrap applications.

The need for a

```bash

pip install marlin

marlin start

marlin stats

marlin stop

marlin restart

marlin runserver
```


| METHOD        | URL                               | RESPONSE    |  DESCRIPTION |
| ------------- |:--------------------------------: | :----------:| :-----------:|
| GET           | /api/v1/<model>/?start=0&end=10   |[data] (0-10)|
| GET           | /api/v1/<model>/1                 |  data item  |
| POST          | /api/v1/<model>/                  |    [data]   |
| GET           | /api/v1/<model>/                  |    [data]   |
| GET           | /api/v1/<model>/                  |    [data]   |
| GET           | /api/v1/<model>/                  |    [data]   |

```config
[SERVER]
DEBUG=True
PID_FILE = '/tmp/marlin.pid'
LOG_FILE = '/tmp/marlin.log'

[REDIS]
REDIS_SERVER = localhost
REDIS_PORT = 6379
API_PREFIX = /api/

[APP]
APP_NAME = marlin
```