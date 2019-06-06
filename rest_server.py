#!/usr/bin/env python

'''
https://gist.github.com/tliron/8e9757180506f25e46d9

Simple and functional REST server for Python (2.7) using no dependencies beyond the Python standard library.
Features:
* Map URI patterns using regular expressions
* Map any/all the HTTP VERBS (GET, PUT, DELETE, POST)
* All responses and payloads are converted to/from JSON for you
* Easily serve static files: a URI can be mapped to a file, in which case just GET is supported
* You decide the media type (text/html, application/json, etc.)
* Correct HTTP response codes and basic error messages
* Simple REST client included! use the rest_call_json() method
As an example, let's support a simple key/value store. To test from the command line using curl:
curl "http://localhost:8080/records"
curl -X PUT -d '{"name": "Tal"}' "http://localhost:8080/record/1"
curl -X PUT -d '{"name": "Shiri"}' "http://localhost:8080/record/2"
curl "http://localhost:8080/records"
curl -X DELETE "http://localhost:8080/record/2"
curl "http://localhost:8080/records"
Create the file web/index.html if you'd like to test serving static files. It will be served from the root URI.
@author: Tal Liron (tliron @ github.com)
'''

import sys, os, re, shutil, json, urllib, urllib2, BaseHTTPServer

# Fix issues with decoding HTTP responses
reload(sys)
sys.setdefaultencoding('utf8')

current_dir = os.path.dirname(os.path.realpath(__file__))
records = {}
pls_list = {}
pls_dir = "/home/pi/playlist"

def get_pls_list(handler):
    pls_arr = []
    for entry in os.listdir(pls_dir):
        if os.path.isfile(os.path.join(pls_dir, entry)):
            print(entry)
            pls_arr.append(entry)
    pls_arr.sort()
    i = 0
    pls_list.clear()
    for pls in pls_arr:
        pls_list[i] = pls
        i += 1
    return pls_list

def play(handler):
    return None

def get_records(handler):
    return "OK"

def get_record(handler):
    key = urllib.unquote(handler.path[8:])
    return records[key] if key in records else None

def set_record(handler):
    key = urllib.unquote(handler.path[8:])
    payload = handler.get_payload()
    records[key] = payload
    return records[key]

def delete_record(handler):
    key = urllib.unquote(handler.path[8:])
    del records[key]
    return True # anything except None shows success

def rest_call_json(url, payload=None, with_payload_method='PUT'):
    'REST call with JSON decoding of the response and JSON payloads'
    if payload:
        if not isinstance(payload, basestring):
            payload = json.dumps(payload)
        # PUT or POST
        response = urllib2.urlopen(MethodRequest(url, payload, {'Content-Type': 'application/json'}, method=with_payload_method))
    else:
        # GET
        response = urllib2.urlopen(url)
    response = response.read().decode()
    return json.loads(response)

class MethodRequest(urllib2.Request):
    'See: https://gist.github.com/logic/2715756'
    def __init__(self, *args, **kwargs):
        if 'method' in kwargs:
            self._method = kwargs['method']
            del kwargs['method']
        else:
            self._method = None
        return urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self, *args, **kwargs):
        return self._method if self._method is not None else urllib2.Request.get_method(self, *args, **kwargs)

class RESTRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.routes = {
            r'^/$': {'file': 'web/index.html', 'media_type': 'text/html'},
            r'^/records$': {'GET': get_records, 'media_type': 'application/json'},
            r'^/pls_list$': {'GET': get_pls_list, 'media_type': 'application/json'},
            r'^/play$': {'GET': play, 'media_type': 'application/json'},
            r'^/record/': {'GET': get_record, 'PUT': set_record, 'DELETE': delete_record, 'media_type': 'application/json'}
            }
        
        return BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
    
    def do_HEAD(self):
        self.handle_method('HEAD')
    
    def do_GET(self):
        self.handle_method('GET')

    def do_POST(self):
        self.handle_method('POST')

    def do_PUT(self):
        self.handle_method('PUT')

    def do_DELETE(self):
        self.handle_method('DELETE')
    
    def get_payload(self):
        payload_len = int(self.headers.getheader('content-length', 0))
        payload = self.rfile.read(payload_len)
        payload = json.loads(payload)
        return payload
        
    def handle_method(self, method):        
        route = self.get_route()        
        if route is None:
            self.send_response(404)
            self.end_headers()
            self.wfile.write('Route not found\n')
        else:
            print "method: " + method + ", route: " + str(route)
            if method == 'HEAD':
                self.send_response(200)
                if 'media_type' in route:
                    self.send_header('Content-type', route['media_type'])
                self.end_headers()
            else:
                if 'file' in route:
                    if method == 'GET':
                        try:
                            f = open(os.path.join(current_dir, route['file']))
                            try:
                                self.send_response(200)
                                if 'media_type' in route:
                                    self.send_header('Content-type', route['media_type'])
                                self.end_headers()
                                shutil.copyfileobj(f, self.wfile)
                            finally:
                                f.close()
                        except:
                            self.send_response(404)
                            self.end_headers()
                            self.wfile.write('File not found\n')
                    else:
                        self.send_response(405)
                        self.end_headers()
                        self.wfile.write('Only GET is supported\n')
                else:
                    if method in route:
                        content = route[method](self)
                        if content is not None:
                            self.send_response(200)
                            if 'media_type' in route:
                                self.send_header('Content-type', route['media_type'])
                            self.end_headers()
                            if method != 'DELETE':
                                self.wfile.write(json.dumps(content))
                        else:
                            self.send_response(404)
                            self.end_headers()
                            self.wfile.write('Not found\n')
                    else:
                        self.send_response(405)
                        self.end_headers()
                        self.wfile.write(method + ' is not supported\n')
                    
    
    def get_route(self):
        for path, route in self.routes.iteritems():
            if re.match(path, self.path):
                return route
        return None

    def handle_get(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        path = "/index.html"
        if self.path != "/":
            path = self.path
        print "path: " + path + ", dir_path: " + dir_path + ", path: " + dir_path + path
        print "exists: " + str(os.path.isfile(dir_path + path))
        exists = os.path.isfile(dir_path + path)
        if not exists and path == "/favicon.ico":
            self.send_response(404)
            self.end_headers()
            return
        try:
            if exists:
                print "open: " + dir_path + path
                f = open(dir_path + path)
                try:
                    # while True:
                    #     file_data = f.read(32768)
                    #     if file_data is None or len(file_data) == 0:
                    #         break
                    #     self.wfile.write(file_data) 
                    # f.close()
                    self.send_response(200)
                    if paths.split(".")[-1] == "html" or paths.split(".")[-1] == "htm":
                        self.send_header("Content-type", "text/html")
                    if paths.split(".")[-1] == "css":
                        self.send_header("Content-type", "text/css")
                    self.end_headers()
                    # self.wfile.write("<html><head><title>Title goes here.</title></head><body>TEST</body>")
                    while True:
                        file_data = f.read(32768)
                        if file_data is None or len(file_data) == 0:
                            break
                        self.wfile.write(file_data) 
                    f.close()
                except Exception, e:
                    print "EXCEPTION:" + e
                    self.send_response(400)
                finally:
                    f.close()
                    return

            print "File not found"

            route = self.get_route()        
            if route is None:
                self.send_response(404)
                self.end_headers()
                self.wfile.write('Route not found\n')
            f = open(os.path.join(current_dir, route['file']))
            try:
                self.send_response(200)
                if 'media_type' in route:
                    self.send_header('Content-type', route['media_type'])
                self.end_headers()
                shutil.copyfileobj(f, self.wfile)
            finally:
                f.close()
        except:
            self.send_response(404)
            self.end_headers()
            self.wfile.write('File not found\n')

def rest_server(port):
    'Starts the REST server'
    http_server = BaseHTTPServer.HTTPServer(('', port), RESTRequestHandler)
    print 'Starting HTTP server at port %d' % port
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
    print 'Stopping HTTP server'
    http_server.server_close()

def main(argv):
    rest_server(6707)

if __name__ == '__main__':
    main(sys.argv[1:])