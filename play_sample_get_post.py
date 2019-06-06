#!/usr/bin/env python
import json, cgi, cgitb

req = cgi.FieldStorage()
test_value = req.getvalue("test")

resp = {}

if test_value is not None:
    resp[0] = "got POST request"
    resp[1] = test_value
else:
    resp[0] = "this is GET test"

# print "Content-type: text/json"
print json.dumps(resp)