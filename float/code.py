import supervisor

supervisor.runtime.autoreload = False

import os
import socketpool
import json
import wifi
import rtc
import time

import peripherals
import board



from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.methods import HTTPMethod

ssid = "1306-2"
password = "66gaf58ee4"

print("Connecting to", ssid)
wifi.radio.connect(ssid, password)
print("Connected to", ssid)
pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool, "/static")

i2c = board.I2C()
bno, step = peripherals.get_peripherals(i2c)
stepsTaken = 0
status = 0


@server.route("/")
def base(request: HTTPRequest):
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:

        response.send_file("index.html")

@server.route("/step",HTTPMethod.POST)
def stepHtml(request: HTTPRequest):
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        stepdata = request.body.decode().split("&")
        print(stepdata[0].split("=")[1])
        print(stepdata[1].split("=")[1])
        step.move(int(stepdata[0].split("=")[1]),int(stepdata[1].split("=")[1]))
        stepsTaken=+int(stepdata[0].split("=")[1])
        response.send("Succses")
        

@server.route("/sync",HTTPMethod.POST)
def setTime(request: HTTPRequest):
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        #do thing
        response.send("Succses")

@server.route("/getInfoBrowser",HTTPMethod.GET)
def getInfoWebpage(request: HTTPRequest):
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        r = rtc.RTC()
        current_time = r.datetime
        output = '''<!DOCTYPE html>
<head>
    <title>mateSUb UI</title>
        <meta encoding=utf-8>
        <meta http-equiv="refresh" content="5" >
</head>
<body>'''
        output += "<table><tr><th>Time</th><td>" + f'{current_time.tm_hour:02d}' + ":" + f'{current_time.tm_min:02d}' +":"+ f'{current_time.tm_sec:02d}' + "</td></tr>"
        output += "<tr><th>Team Name</th><td>One Degree North</td></tr></table></body>"
        response.send(output)

@server.route("/getInfoJson",HTTPMethod.GET)
def getInfoJson(request: HTTPRequest):
    info_dict = {"time":"","teamName":"One Degree North","euler":bno.euler,"linearAccel":bno.linear_acceleration,"status":status,"steps":stepsTaken}
    r = rtc.RTC()
    current_time = r.datetime
    info_dict["time"] = f'{current_time.tm_hour:02d}' + ":" + f'{current_time.tm_min:02d}' +":"+ f'{current_time.tm_sec:02d}'
    with HTTPResponse(request, content_type=MIMEType.TYPE_JSON) as response:
        response.send(json.dumps(info_dict))


   
print(f"Listening on http://{wifi.radio.ipv4_address}:80")


# Start the server.

server.start(str(wifi.radio.ipv4_address))
status=1



while True:

    try:

        # Do something useful in this section,

        # for example read a sensor and capture an average,

        # or a running total of the last 10 samples


        # Process any waiting requests

        server.poll()

    except OSError as error:

        print(error)

        continue
