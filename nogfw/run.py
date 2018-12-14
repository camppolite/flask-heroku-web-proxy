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


@app.route('/proxy', methods=["GET", "POST", "PUT", "DELETE"])
def proxy_req():
    """根据输入的url，通过服务器获取url再返回给客户端"""
    if request.method == 'POST':
        url = request.form["url"]
        if not url:
            return render_template('index.html')
        print(url)
        req = requests.get(url, stream=True)
        return Response(stream_with_context(req.iter_content()), content_type=req.headers['content-type'])

    return render_template('index.html')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=DEBUG_FLAG, host='0.0.0.0', port=LISTEN_PORT)
