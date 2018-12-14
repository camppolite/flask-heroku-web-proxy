"""
A simple proxy server. Usage:
http://hostname:port/p/(URL to be proxied, minus protocol)
For example:
http://localhost:8080/p/www.google.com
"""

import re
from flask import Flask, render_template, request, abort, Response, redirect,make_response, stream_with_context
import requests
import logging

app = Flask(__name__)

# Default Configuration
DEBUG_FLAG = True
LISTEN_PORT = 51216

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("main.py")


@app.route('/proxy/<path:url>', methods=["GET", "POST", "PUT", "DELETE"])
def proxy(url):
    """Fetches the specified URL and streams it out to the client.
    If the request was referred by the proxy itself (e.g. this is an image fetch for
    a previously proxied HTML page), then the original Referer is passed."""
    url = re.sub('/proxy/', "", request.full_path)
    print(url)
    print(request.method)
    req = requests.get(url, stream=True)
    return Response(stream_with_context(req.iter_content()), content_type=req.headers['content-type'])


@app.route('/')
def index():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=DEBUG_FLAG, host='0.0.0.0', port=LISTEN_PORT)
