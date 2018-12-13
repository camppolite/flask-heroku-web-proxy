"""
A simple proxy server. Usage:
http://hostname:port/p/(URL to be proxied, minus protocol)
For example:
http://localhost:8080/p/www.google.com
"""
import os
from flask import Flask, render_template, request, abort, Response, redirect
from werkzeug.serving import WSGIRequestHandler
import requests
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("main.py")


@app.route('/<path:url>')
def root(url):
    LOG.info("Root route, path: %s", url)
    # If referred from a proxy request, then redirect to a URL with the proxy prefix.
    # This allows server-relative and protocol-relative URLs to work.
    proxy_ref = proxy_ref_info(request)
    if proxy_ref:
        redirect_url = "%s/%s%s" % (proxy_ref[0], url, ("?" + request.query_string if request.query_string else ""))
        LOG.info("Redirecting referred URL to: %s", redirect_url)
        return proxy(redirect_url)
    abort(404)


@app.route('/p/<path:url>')
def proxy(url):
    """Fetches the specified URL and streams it out to the client.
    If the request was referred by the proxy itself (e.g. this is an image fetch for
    a previously proxied HTML page), then the original Referer is passed."""
    r = get_source_rsp(url)
    LOG.info("Got %s response from %s",r.status_code, url)
    headers = dict(r.headers)
    if headers.has_key('transfer-encoding'):
        del(headers['transfer-encoding'])
    if headers.has_key('content-encoding'):
        del(headers['content-encoding'])
    return Response(r.content, headers = headers)


def get_source_rsp(url):
        url = 'http://%s' % url
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
    port = int(os.environ.get('PORT', 5000))
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(host='0.0.0.0', port=port)
