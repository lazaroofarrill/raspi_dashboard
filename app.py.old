from flask import Flask
from flask_sockets import Sockets
from threading import Thread
import time

BUTTON_PIN = 23
LED_PIN = 22
SOUND_PIN = 18


def read_button_value():
    return GPIO.input(BUTTON_PIN)

class ButtonThread(Thread):
    def __init__(self):
        super(ButtonThread, self).__init__()

    def run(self):
        while True:
            button_value = read_button_value()
            print(button_value)
            time.sleep(0.02)

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

app = Flask(__name__)

sockets = Sockets(app)

@app.route("/button-value")
def get_button_value():
    return str(read_button_value())

@app.route("/sound")
def sound():
    for x in range(10):
    	GPIO.output(SOUND_PIN, 1)
    	time.sleep(0.5)
    	GPIO.output(SOUND_PIN, 0)
    	#return "ok"

@app.route("/led")
def toggle_led():
    GPIO.output(LED_PIN, not GPIO.input(LED_PIN))
    return str(GPIO.input(LED_PIN))


@sockets.route("/l1")
def l1_socket(ws):
    while not ws.closed:
        message = ws.receive()
        ws.send(message)

   
@app.route("/l1")
def toggle_l1():
    pass




if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([LED_PIN, SOUND_PIN], GPIO.OUT)
    GPIO.setup(BUTTON_PIN, GPIO.IN)

    button_thread = ButtonThread()
    button_thread.start()

        
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
