import time
import Adafruit_BMP.BMP085 as BMP085

from flask import Flask
from flask_cors import CORS

BUTTON_PIN = 23
LED_PIN = 22
SOUND_PIN = 18
RELAY_PIN = 12

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
    print(str(value))
    if value == "on":
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
    GPIO.setup([LED_PIN, SOUND_PIN, RELAY_PIN], GPIO.OUT)
    GPIO.setup(BUTTON_PIN, GPIO.IN)

    GPIO.output(RELAY_PIN, 0)

    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
