# import the necessary packages
from imutils.video import VideoStream
from flask import Flask, Response, redirect, render_template, request, url_for
from tinydb import TinyDB, Query
import os, threading, argparse
import time
from datetime import datetime
import cv2, imutils
import requests, json

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()
luz = False
requests.get('https://maker.ifttt.com/trigger/luz_oreo_off/with/key/cH3SQhVCJgHGjDk0qMStUu')

'''
eyJhbGciOiJSUzI1NiIsImtpZCI6Ijc5YzgwOWRkMTE4NmNjMjI4YzRiYWY5MzU4NTk5NTMwY2U5MmI0YzgiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXpwIjoiNjQzODY0NDU5OTczLXZtNDhpZmU3djVrMWRtbWluODBmZjRyYnFuODJuYzB0LmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwiYXVkIjoiNjQzODY0NDU5OTczLXZtNDhpZmU3djVrMWRtbWluODBmZjRyYnFuODJuYzB0LmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwic3ViIjoiMTAxOTYzMjY5MzAyNzc1NzQ4Mjk0IiwiaGQiOiJtZWxpZ3JhbmFtYWlsLmNvbSIsImVtYWlsIjoibWF0ZW9AbWVsaWdyYW5hbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXRfaGFzaCI6ImU4UWVsVVhEanlkaEIwS1JOaXZneFEiLCJuYW1lIjoiTWF0ZW8gUGVyaWFnbyIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS0vQUF1RTdtQXd3MEZTYjM3dGdpVE9JU1gxeGluQzc3aTg0bEJuR2tBVGwwcjI9czk2LWMiLCJnaXZlbl9uYW1lIjoiTWF0ZW8iLCJmYW1pbHlfbmFtZSI6IlBlcmlhZ28iLCJsb2NhbGUiOiJlbiIsImlhdCI6MTU4MjMxNjA4NywiZXhwIjoxNTgyMzE5Njg3LCJqdGkiOiI0ZGNjNWRkYTlkMzg0NWUwYTFhNjRhYmU1YzQwYWRkOTliYjJhODA4In0.r8r0KOQVlRfW6Up9Ze3jdOuK2KtEFOwroRNQ8mm2cwZjiyXZUMZ4qXNvN5-F812ZbCkWHLAdWERwwouVcJ9KlWIQmmsZIymXn5qzAKoJdeynBlUWmhMGPk-aWlYhh1197AqzunlRsqxkCyXtaCB9Px5S1sZwa8hZzVulJQyO5sutr6zfdN6HGxhZo1Wd_9hmx2jGTVcoREU-zz6VFtKdCAt197oqOdgdw_U-jPjwWY0SVHBINVGckY7vM0VfXdhm1GUQHpBSruIiC5-9UmzPcgNrQopxTIYhTSuVUZJr2B67hzQS5PBojvZemHYsi-ktFADHeCkjRwugvB9VQ_FmmQ
'''

messages_db = TinyDB('messages_db.json')

# initialize a flask object
app = Flask(__name__)

# initialize the video stream and allow the camera sensor to warmup
vs = cv2.VideoCapture(1)
time.sleep(2.0)

@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")

@app.route("/switch_light")
def switch_light():
    # switch light
    global luz
    luz = not luz
    # REFACTOR PLEASE
    if luz:
        s = 'on'
    else:
        s = 'off'
    print('la luz esta ', s)
    requests.get('https://maker.ifttt.com/trigger/luz_oreo_{}/with/key/cH3SQhVCJgHGjDk0qMStUu'.format(s))
    time.sleep(5.0) # time for light to switch
    return "done" #("nothing")

@app.route('/post_message', methods=['POST'])
def post_message():
    data = request.get_json(force=True)
    # datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    messages_db.insert({'Username': data[0], 'Message': data[1], 'Timestamp': data[2]})
    return 'Message sent!'

@app.route('/retrieve_messages', methods=['GET', 'POST'])
def retrieve_messages():
    data = request.get_json(force=True)
    n = int(data[0])
    newest_msg = sorted(messages_db.all(), key=lambda k: k['Timestamp'])[:n]
    html = ''
    for m in newest_msg:
        html = html + ("<div class='msgln'>({}) <b>{}</b>: {}<br></div>".format(
            datetime.fromtimestamp(m['Timestamp']/1000).strftime("%H:%M"), m['Username'], m['Message'])) # timestamp / 1000 to convert to seconds
    return json.dumps(html)

@app.route("/purge_db")
def purge_db():
    messages_db.purge()
    return ("nothing")

'''
@app.route("/restart")
def index():
    # restart the program.
    os.execl("C:\\Users\\mateo\\Google Drive\\dev\\python\\opencv\\webstreaming.py", "")
'''

def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if not vs.isOpened():
                raise IOError("Cannot open webcam")
            (grabbed, outputFrame) = vs.read()
            if outputFrame is None:
                print('no frame :(')
                continue

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            # ensure the frame was successfully encoded
            if not flag:
                print('frame not encoded :(')
                continue

        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    print('getting feed...')
    return Response(generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
        help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
        help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
        help="# of frames used to construct the background model")
    args = vars(ap.parse_args())

    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True,
        threaded=True, use_reloader=False)
