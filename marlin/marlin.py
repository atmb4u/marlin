# -*- coding: utf-8 -*-
#!/usr/bin/env python

from functools import wraps, update_wrapper
from datetime import timedelta
import ConfigParser

import ujson as json
from redis import Redis, ConnectionError

from flask import make_response, request, current_app, Response, Flask, render_template, url_for

VERSION = "0.979"

config = ConfigParser.ConfigParser()
config.read("marlin.config")

if config.has_option("SERVER", "DEBUG"):
    DEBUG = config.get("SERVER", "DEBUG")
else:
    DEBUG = True
if config.has_option("REDIS", "REDIS_SERVER"):
    REDIS_SERVER = config.get("REDIS", "REDIS_SERVER")
else:
    REDIS_SERVER = "127.0.0.1"
if config.has_option("REDIS", "REDIS_PORT"):
    REDIS_PORT = config.get("REDIS", "REDIS_PORT")
else:
    REDIS_PORT = "6379"
if config.has_option("REDIS", "API_PRIFIX"):
    API_PREFIX = config.get("REDIS", "API_PREFIX")
else:
    API_PREFIX = '/api/'
if config.has_option("APP", "APP_NAME"):
    APP_NAME = config.get("APP", "APP_NAME")
else:
    APP_NAME = "marlin"
if config.has_option("REDIS", "REDIS_PASSWORD"):
    REDIS_PASSWORD = config.get("REDIS", "REDIS_PASSWORD")
else:
    REDIS_PASSWORD = ""

app = Flask(__name__)
app.debug = DEBUG


def cross_domain(origin=None, methods=None, headers=None,
                 max_age=21600, attach_to_all=True,
                 automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods
        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp
            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator


def returns_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type='application/json; charset=utf-8')

    return decorated_function


@app.route("/")
def index():
    url_for('static', filename='toast.css')
    url_for('static', filename='marlin.jpg')
    return render_template('index.html')


def unified_router(rdm):
    """
    used by uni_api_router and multi_api_router.
    input: a RedisDatabaseManager instance
    output: http response with/without data with responses accordingly.
        with data : 200
        Data not found: 404
    """
    error_response = Response(json.dumps(
        {'status': "Make sure redis-server is installed and running on http://%s:%s" % (REDIS_SERVER, REDIS_PORT)}),
        content_type='application/json; charset=utf-8', status=500)
    if rdm:
        rdm.manipulate_data()
    else:
        return error_response
    if rdm.status:
        if rdm.data:
            #TODO: add list and item views for data in html
            return Response(rdm.string_data, content_type='application/json; charset=utf-8')
        elif rdm.method == "DELETE":
            return Response("", status=200, content_type='application/json; charset=utf-8')
        else:
            return Response(json.dumps({'status': "No data Found"}), content_type='application/json; charset=utf-8',
                            status=404)
    else:
        return error_response


@returns_json
@app.route(API_PREFIX + '<version>/<model>/<id>', methods=['GET', 'OPTIONS', 'POST', 'PUT', 'DELETE'])
@app.route(API_PREFIX + '<version>/<model>/<id>/', methods=['GET', 'OPTIONS', 'POST', 'PUT', 'DELETE'])
@cross_domain(origin='*')
def uni_api_router(version, model, id):
    rdm = RedisDatabaseManager(request, version, model, id)
    return unified_router(rdm)


@returns_json
@app.route(API_PREFIX + '<version>/<model>', methods=['GET', 'OPTIONS', 'POST', 'PUT', 'DELETE'])
@app.route(API_PREFIX + '<version>/<model>/', methods=['GET', 'OPTIONS', 'POST', 'PUT', 'DELETE'])
@cross_domain(origin='*')
def multi_api_router(version, model):
    rdm = RedisDatabaseManager(request, version, model, None)
    return unified_router(rdm)


@app.route("/ping/")
def ping():
    """
    Service used to check if the connection to redis server is intact and redis server is working well.
    """
    r = Redis(host=REDIS_SERVER, port=REDIS_PORT, password=REDIS_PASSWORD)
    try:
        r.ping()
        return Response("", status=200)
    except ConnectionError:
        return Response("", status=500)


class RedisDatabaseManager(object):
    """
    manages all the http requests and routes in the backend for GET, DELETE or PUT operation
    accordingly.

    """

    r = Redis(host=REDIS_SERVER, port=REDIS_PORT, password=REDIS_PASSWORD)
    app_name = APP_NAME

    def __init__(self, request, version, model, id):
        self.request = request
        self.version = version
        self.model = model
        self.id = id
        self.method = request.method
        self.key = "%s.%s.%s" % (self.app_name, self.version, self.model)
        self.status = False
        self.data = None
        self.string_data = ""
        self.length = 0

    def init_db(self):
        try:
            length = self.r.get(self.key + "_counter")
            if length:
                self.length = int(length)
        except ConnectionError:
            return False

    def manipulate_data(self):
        self.init_db()
        if self.method == "GET" and self.id:
            return self.get_from_redis()
        elif self.method == "GET" and not self.id:
            start = int(self.request.args.get("start", 1))
            end = int(self.request.args.get("end", self.length))
            return self.get_many_from_redis(start, end)
        elif (self.method == "POST" or self.method == "OPTIONS") and (not self.id or self.id == "add"):
            return self.set_to_redis()
        elif self.method == "DELETE" and self.id:
            self.delete_from_redis()
        elif self.method == "DELETE" and not self.id:
            if self.request.form.get("force") == "1":
                return self.flush_model()
            else:
                return self.delete_all_from_redis()
        elif (self.method == "PUT" or self.method == "POST") and self.id:
            return self.update_to_redis()

    def set_to_redis(self):
        try:
            kv_dict = {}
            for key in self.request.form.keys():
                try:
                    kv_dict[key] = float(self.request.form.get(key))
                    if int(kv_dict[key]) == kv_dict[key]:
                        kv_dict[key] = int(self.request.form.get(key))
                except ValueError:
                    kv_dict[key] = self.request.form.get(key)
            kv_dict['id'] = self.length + 1
            self.string_data = json.dumps(kv_dict)
            self.r.hset(self.key, self.length + 1, self.string_data)
            self.r.incr(self.key + "_counter")
            self.data = kv_dict
            self.status = True
        except ConnectionError:
            self.status = False

    def get_from_redis(self):
        try:
            self.data = self.r.hget(self.key, self.id)
            self.string_data = self.data
            self.status = True
        except ConnectionError:
            self.status = False

    def get_many_from_redis(self, start, end):
        try:
            id_list = range(start, end + 1)
            object_list = []
            if id_list:
                data_list = self.r.hmget(self.key, id_list)
                for item in data_list:
                    if item:
                        object_list.append(json.loads(item))
            self.data = object_list
            self.string_data = json.dumps(object_list)
            self.status = True
        except ConnectionError:
            self.status = False

    def delete_from_redis(self):
        try:
            self.r.hdel(self.key, self.id)
            self.status = True
        except ConnectionError:
            self.status = False

    def delete_all_from_redis(self):
        try:
            id_list = range(1, self.length + 1)
            for identity in id_list:
                self.r.hdel(self.key, identity)
            self.status = True
        except ConnectionError:
            self.status = False

    def update_to_redis(self):
        try:
            kv_dict = {}
            for key in self.request.form.keys():
                kv_dict[key] = self.request.form.get(key)
            kv_dict['id'] = self.id
            self.string_data = json.dumps(kv_dict)
            self.r.hset(self.key, self.id, self.string_data)
            self.data = kv_dict
            self.status = True
        except ConnectionError:
            self.status = False

    def flush_model(self):
        try:
            self.delete_all_from_redis()
            self.r.set(self.key + "_counter", 0)
            self.status = True
        except ConnectionError:
            self.status = False