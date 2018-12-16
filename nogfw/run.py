#!/usr/bin/env python

# from boto.s3.connection import S3Connection
# s3 = S3Connection(os.environ['S3_KEY'], os.environ['S3_SECRET'])
from flask import (
    Flask, render_template, request, abort, Response, redirect,make_response, stream_with_context, url_for
)
import requests
import logging
import re

app = Flask(__name__)

# Default Configuration
DEBUG_FLAG = True
LISTEN_PORT = 51216

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("main.py")


@app.route('/proxy/<path:url>', methods=["GET", "POST", "PUT", "DELETE"])
def proxy(url):
    """根据输入的url，通过服务器获取url再返回给客户端"""
    if not url:
        return render_template('index.html')
    print("访问网址：" + url)
    try:
        req = requests.get(url, stream=True)
        print("访问状态：%s" % req.status_code)
    except requests.exceptions.ConnectionError as e:
        print(str(e))
        abort(404)
    else:
        return Response(stream_with_context(req.iter_content()), content_type=req.headers['content-type'])


@app.route('/no_js', methods=["GET", "POST"])
def no_js():
    """获取用户输入的url，重定向到代理网址"""
    if request.method == 'POST':
        url = request.form["url"]
        if not url:
            return render_template('index.html')
        print(url)
        return redirect(url_for('proxy', url=url))

    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=DEBUG_FLAG, host='0.0.0.0', port=LISTEN_PORT)
