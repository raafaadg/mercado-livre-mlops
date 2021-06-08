import json
from werkzeug.exceptions import abort
from flask import Response

def api_response(resp_dict, status_code):
    response = Response(json.dumps(resp_dict), status_code)
    response.headers["Content-Type"] = "application/json"
    return response
