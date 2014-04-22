#!/usr/bin/python
import ConfigParser
import logging

from daemon import runner
import sys

if len(sys.argv) == 2 and 'live' == sys.argv[1]:
    from marlin import app
else:
    from marlin.marlin import app

try:
    from marlin_functions import *
    import inspect
    import marlin_functions
    funcs = [func[0] for func in inspect.getmembers(marlin_functions, inspect.isfunction)]
    if funcs:
        print("Custom Functions defined:", funcs)
except:
    print("No custom functions defined.\n Check atmb4u.github.io/marlin for more details on custom functions.")

config = ConfigParser.ConfigParser()
config.read("marlin.config")

if config.has_option("SERVER", "LOG_FILE"):
    LOG_FILE = config.get("SERVER", "LOG_FILE")
else:
    LOG_FILE = "/tmp/marlin.log"
if config.has_option("SERVER", "PID_FILE"):
    PID_FILE = config.get("SERVER", "PID_FILE")
else:
    PID_FILE = "/tmp/marlin.pid"
if config.has_option("SERVER", "SERVER_PORT"):
    SERVER_PORT = int(config.get("SERVER", "SERVER_PORT"))
else:
    SERVER_PORT = 5000

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)


class MarlinServer():

    def __init__(self, pidfile='/tmp/', stderr='/dev/null', stdout='/dev/null'):
        self.stdin_path = '/dev/null'
        self.stdout_path = stdout
        self.stderr_path = stderr
        self.pidfile_path = pidfile
        self.pidfile_timeout = 5

    @staticmethod
    def run():

        app.run(port=SERVER_PORT)


if __name__ == "__main__":
    marlin_server = MarlinServer(pidfile=PID_FILE)
    if len(sys.argv) == 2 and 'live' == sys.argv[1]:
        print "Starting Test Server ..."
        app.debug = True
        app.run(port=SERVER_PORT)
        sys.exit(0)
    runner = runner.DaemonRunner(marlin_server)
    runner.do_action()
