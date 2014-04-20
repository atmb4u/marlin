"""
These are examples to get started with creating custom functions in marlin.
simple  - A very simple request - response

"""

import json
from marlin import app, RedisDatabaseManager
from flask import Response, request


@app.route("/simple/")
def simple():
    return Response("Simple Custom Response")


@app.route("/simple_get/<model>/")
def simple_get(model):
    rdm = RedisDatabaseManager(request, model=model)
    if rdm:
        rdm.manipulate_data()
        user_id = 1
        rdm.id = user_id
        rdm.get_from_redis()  # get data for the specific user id
    else:
        return json.dumps({"status": "Something is not right"})
    if rdm.status and rdm.data:
        return Response(rdm.string_data, content_type='application/json; charset=utf-8')
    elif rdm.status:
        return Response(json.dumps({'status': "No data Found"}), content_type='application/json; charset=utf-8',
                        status=404)
    else:
        return json.dumps({"status": "Something is not right"})


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
                if datum.get("name") == "Orange":
                    custom_query_set.append(datum)
            return Response(json.dumps(custom_query_set), content_type='application/json; charset=utf-8')
        else:
            return Response(json.dumps({'status': "No data Found"}), content_type='application/json; charset=utf-8',
                            status=404)
    else:
        return error_response
