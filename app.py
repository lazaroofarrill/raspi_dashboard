import time
from threading import Thread

import Adafruit_BMP.BMP085 as BMP085
from flask import Flask
from flask_cors import CORS

BUTTON_PIN = 26
LED_PIN = 16
LED_HIGH = 19
SOUND_PIN = 18
RELAY_PIN = 15

emergency_stop = False


class EmergencyStopThread(Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        print("Starting emergency stop routine")
        while True:
            if emergency_stop:
                GPIO.output(RELAY_PIN, 0)


class LedWatchThread(Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        print("Starting led watch routine")
        while True:
            if emergency_stop or True:
                GPIO.output(LED_PIN, 1)
                time.sleep(1)
                GPIO.output(LED_PIN, 0)
                time.sleep(1)
            else:
                GPIO.output(LED_PIN, 0)


class ButtonWatchThread(Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        global emergency_stop
        print("Starting button watch routine")
        while True:
            print(GPIO.input(BUTTON_PIN))
            time.sleep(0.1)
            button_value = GPIO.input(BUTTON_PIN)
            if not button_value:
                emergency_stop = not emergency_stop


sensor = BMP085.BMP085(busnum=1)

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print(
        "Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")


def read_button_value():
    return GPIO.input(BUTTON_PIN)


app = Flask(__name__)
CORS(app)


@app.route("/button-value")
def get_button_value():
    return str(read_button_value())


@app.route("/sound")
def sound():
    for x in range(10):
        GPIO.output(SOUND_PIN, 1)
        time.sleep(0.5)
        GPIO.output(SOUND_PIN, 0)


@app.route("/led")
def toggle_led():
    GPIO.output(LED_PIN, not GPIO.input(LED_PIN))
    return str(GPIO.input(LED_PIN))


@app.route("/fan/<value>")
def switch_fan(value):
    if value == "on" and (not emergency_stop):
        GPIO.output(RELAY_PIN, 1)
    elif value == "off":
        GPIO.output(RELAY_PIN, 0)
    return str(GPIO.input(RELAY_PIN))


@app.route("/readings")
def get_readings():
    pressure = sensor.read_pressure()
    temperature = sensor.read_temperature()
    sealevel_pressure = sensor.read_sealevel_pressure()
    altitude = sensor.read_altitude()

    readings = {
        "pressure": pressure,
        "temperature": temperature,
        "sealevel_pressure": sealevel_pressure,
        "altitude": altitude
    }
    return readings


if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([LED_PIN, LED_HIGH, SOUND_PIN, RELAY_PIN], GPIO.OUT)
    GPIO.setup(BUTTON_PIN, GPIO.IN)

    GPIO.output(RELAY_PIN, 0)
    GPIO.output(LED_HIGH, 0)

    # Threads
    emergency_stop_thread = EmergencyStopThread()
    led_watch_thread = LedWatchThread()
    button_watch_thread = ButtonWatchThread()

    emergency_stop_thread.start()
    led_watch_thread.start()
    button_watch_thread.start()

    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
