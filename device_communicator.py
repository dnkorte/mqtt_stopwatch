"""
# MQTT-based stopwatch / status display for robots and similar devices
#
# Author(s):    Don Korte
#               http://donstechstuff.com/
# github:       https://github.com/dnkorte/
#
# Module: device_communicator.py
#
# MIT License
#
# Copyright (c) 2022 Don Korte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""

import board
import busio
import digitalio
import time
import neopixel
#from adafruit_esp32spi import adafruit_esp32spi
#from adafruit_esp32spi import adafruit_esp32spi_wifimanager
from adafruit_matrixportal.matrixportal import MatrixPortal
import adafruit_esp32spi.adafruit_esp32spi_socket as socket

import adafruit_minimqtt.adafruit_minimqtt as MQTT

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

class Communicator:
    def __init__(self, matrixportal, message_handler):
        self.matrixportal = matrixportal
        self.message_handler = message_handler
        self.matrixportal.network.connect()
        MQTT.set_socket(socket, self.matrixportal.network._wifi.esp)
        # self.client = MQTT.MQTT(broker=secrets["broker"], port=secrets["port"], is_ssl=False)
        self.client = MQTT.MQTT(broker=secrets["broker"], port=secrets["port"],
            username=secrets["user"], password=secrets["pass"], is_ssl=False)
        self.client.on_connect = connect
        self.client.on_disconnect = disconnected
        self.client.on_subscribe = subscribe
        self.client.on_publish = publish
        self.client.on_message = message_handler
        self.client.connect()

    def subscribe(self, topic):
        self.client.subscribe(topic)

# ------------- MQTT Functions (note these are standalong, not part of class ------------- #

# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connect(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    # print("Connected to MQTT Broker!")
    #print("Flags: {0}\n RC: {1}".format(flags, rc))
    return


def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    # print("Disconnected from MQTT Broker!")
    return


def subscribe(client, userdata, topic, granted_qos):
    # This method is called when the client subscribes to a new feed.
    # print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))
    return


def publish(client, userdata, topic, pid):
    # This method is called when the client publishes data to a feed.
    # print("Published to {0} with PID {1}".format(topic, pid))
    return
