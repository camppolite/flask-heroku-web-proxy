"""
A simple proxy server. Usage:
http://hostname:port/p/(URL to be proxied, minus protocol)
For example:
http://localhost:8080/p/www.google.com
"""
import os
import re
from flask import Flask, render_template, request, abort, Response, redirect,make_response, stream_with_context
from werkzeug.serving import WSGIRequestHandler
import requests
import logging
from contextlib import closing

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("main.py")


# @app.route('/<path:url>')
# def root(url):
#     LOG.info("Root route, path: %s", url)
#     # If referred from a proxy request, then redirect to a URL with the proxy prefix.
#     # This allows server-relative and protocol-relative URLs to work.
#     proxy_ref = proxy_ref_info(request)
#     if proxy_ref:
#         redirect_url = "%s/%s%s" % (proxy_ref[0], url, ("?" + request.query_string if request.query_string else ""))
#         LOG.info("Redirecting referred URL to: %s", redirect_url)
#         return proxy(redirect_url)
#     abort(404)


# @app.before_request
# def before_request():
#     url = request.url
#     method = request.method
#     data = request.data or request.form or None
#     headers = dict()
#     for name, value in request.headers:
#         if not value or name == 'Cache-Control':
#             continue
#         headers[name] = value
#
#     with closing(
#         requests.request(method, url, headers=headers, data=data, stream=True)
#     ) as r:
#         resp_headers = []
#         for name, value in r.headers.items():
#             if name.lower() in ('content-length', 'connection',
#                                 'content-encoding'):
#                 continue
#             resp_headers.append((name, value))
#         return Response(r, status=r.status_code, headers=resp_headers)


@app.route('/proxy/<path:url>')
def proxy(url):
    """Fetches the specified URL and streams it out to the client.
    If the request was referred by the proxy itself (e.g. this is an image fetch for
    a previously proxied HTML page), then the original Referer is passed."""
    # r = get_source_rsp(url)
    # url = url.lstrip('\\')
    # r = requests.get(url)
    # LOG.info("Got %s response from %s",r.status_code, url)
    # headers = dict(r.headers)
    # if headers.has_key('transfer-encoding'):
    #     del(headers['transfer-encoding'])
    # if headers.has_key('content-encoding'):
    #     del(headers['content-encoding'])
    url = re.sub('/proxy/', "", request.full_path)
    print(url)
    req = requests.get(url, stream=True)
    return Response(stream_with_context(req.iter_content()), content_type=req.headers['content-type'])
    # return before_request
    # return make_response(request)
    # return Response(r, r.status_code, headers)


def get_source_rsp(url):
        # url = 'http://%s' % url
        LOG.info("Fetching %s", url)
        # Pass original Referer for subsequent resource requests
        proxy_ref = proxy_ref_info(request)
        headers = { "Referer" : "http://%s/%s" % (proxy_ref[0], proxy_ref[1])} if proxy_ref else {}
        # Fetch the URL, and stream it back
        LOG.info("Fetching with headers: %s, %s", url, headers)
        return requests.get(url, stream=False, params = request.args, headers=headers)


def split_url(url):
    """Splits the given URL into a tuple of (protocol, host, uri)"""
    proto, rest = url.split(':', 1)
    rest = rest[2:].split('/', 1)
    host, uri = (rest[0], rest[1]) if len(rest) == 2 else (rest[0], "")
    return (proto, host, uri)


def proxy_ref_info(request):
    """Parses out Referer info indicating the request is from a previously proxied page.
    For example, if:
        Referer: http://localhost:8080/p/google.com/search?q=foo
    then the result is:
        ("google.com", "search?q=foo")
    """
    ref = request.headers.get('referer')
    if ref:
        _, _, uri = split_url(ref)
        if uri.find("/") < 0:
            return None
        first, rest = uri.split("/", 1)
        if first in "pd":
            parts = rest.split("/", 1)
            r = (parts[0], parts[1]) if len(parts) == 2 else (parts[0], "")
            LOG.info("Referred by proxy host, uri: %s, %s", r[0], r[1])
            return r
    return None


@app.route('/')
def index():
    return 'Hello World!'


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 51216))
    # WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(debug=True, host='0.0.0.0', port=port)
