"""
# MQTT-based stopwatch / status display for robots and similar devices
#
# Author(s):    Don Korte
#               http://donstechstuff.com/
# github:       https://github.com/dnkorte/
#
# Module: code.py
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
# -----------------------------------
# usage: this device responds to MQTT messages on the following topics
#
#   stopwatch/start         (starts timer)
#   stopwatch/stop          (stops timer)

#   stopwatch/clear         (clears the timer display to 0:00,
#                           (and displays title banners on right side
#                           (title banner content can be changed in the config.welcome_banner_1
#                           (and config.welcome_banner_2 variables in the configuration paramters
#
#   robot4/info/status      (assumes message has 2 colon-separated parts,
#                           (program name : statustext
#                           (it displays the statustext on bottom status line (blue)
#                           (it displays the program name on the right panel (orange)
#                           (if possible, it splits long messages at spaces
#
#   robot4/info/warning         (displays messages on bottom status line (red)
#
#   (these messages are specific to PiWars application, but could be modified for other uses)
#   robot4/control/joyYL        (ignores message, just displays "manual driving")
#   robot4/control/joyXL        (ignores message, just displays "manual driving")
#   robot4/control/joyYR        (ignores message, just displays "manual driving")
#   robot4/control/joyXR        (ignores message, just displays "manual driving")
#
#   robot4/info/battvolts
#   currently disabled, but if enabled it expects a message like "11.608 possible_other_text"
#   it displays the voltage (everything before the first space) in bottom status line (green)
#
#   note that the clock is displayed in white text for first 4 minutes
#   then displays as orange from 4m00s until 4m59s, then red after 5m00s
#   this behaviour can be changed in the main while: loop at the bottom of the code
#
#   note that the "info" and "control" topics are prefaced by the name of the
#   "connected device" (shown as "robot4" in the listing above); the device name
#   may be changed in the "config.connected_device" variable in the configuration parameters
#   if you do not have multiple potential devices, the variable may be set to an empty string ""
#
# in addition to this code.py module, the program needs the following modules
# to be in the root directory:
#   (code.py)
#   colors.py
#   device_communicator.py
#   globals.py
#
#   secrets.py  (standard adafruit format, requires at least these parameters:
#               (ssid, password, broker (could be IP address or hostname), port (usually 1883)
#               (if your mqtt broker requires authentication it also needs 'user' and 'pass'
#
# ============== secrets.py should look something like this =============
# (if the broker does not require authentication, the 'user' and 'pass' values
#  may be empty strings, but they must be present)
# ========================================================================
#       secrets = {
#           'ssid' : '_your_ssid_',
#           'password' : '_your_network_password',
#           'timezone' : "America/Detroit", # http://worldtimeapi.org/timezones
#           'broker' : '192.168.86.234',
#           'port' : 1883,
#           'user' : '_your_mqtt_broker_username_',
#           'pass' : '_your_mqtt_broker_password_'
#       }
# =============  end of sample secrets.py ===============================
#
# additionally, this requires the following adafruit libraries in the "lib" folder
#   (note that those with .mpy extension are files, the others are complete folders)
#   adafruit_bus_device
#   adafruit_display_text
#   adafruit_esp32spi
#   adafruit_fakerequests.mpy
#   adafruit_io
#   edafruit_matrixportal
#   adafruit_minimqtt
#   adafruit_oportalbase
#   adafruit_requests.mpy
#   neopixel.mpy
#
# the following adafruit hardware is used:
#   https://www.adafruit.com/product/4745   the matrixportal processor board
#   https://learn.adafruit.com/adafruit-matrixportal-m4  (their learn guide for above)
#   https://www.adafruit.com/product/2278   64x32 RGB LED Matrix 4mm pitch (2 rqd)
#   https://www.adafruit.com/product/4749   acylic diffuser (optional; makes it prettier; 2 needed)
#   (and a 5v 4A power supply with USB-C cable)
#
# you will need to install CircuitPython on the MatrixPortal, per the instructions
# in the learn guide
# -----------------------------------
"""

import time
import board
import terminalio
import displayio
from adafruit_display_text.label import Label
from adafruit_matrixportal.matrixportal import MatrixPortal

from device_communicator import Communicator
import globals
import config
import colors

# --- MatrixPortal setup ---
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, height=32, width=128, debug=False)

# --- Display setup ---
display = matrixportal.display
group = displayio.Group()  # Create a Group
display.show(group)

font = terminalio.FONT

status_text = Label(font, x=2, y=25, color=colors.TFT_BLUE)
group.append(status_text)
status_text.text = ""

mode1_text = Label(font, x=56, y=5, color=colors.TFT_ORANGE)
group.append(mode1_text)
mode1_text.text = config.welcome_banner_1

mode2_text = Label(font, x=56, y=15, color=colors.TFT_ORANGE)
group.append(mode2_text)
mode2_text.text = config.welcome_banner_1

clock_text = Label(font, x=4, y=9, color=colors.TFT_WHITE, scale=2)
group.append(clock_text)
clock_text.text = "0:00"

# --- display a startup message
status_text.text = "Connecting to Network"
status_text.color = color=colors.TFT_GREEN

# --- MQTT messages setup ----
topic_starter = ""
if (len(config.connected_device) >0):
    topic_starter = config.connected_device + "/"

topic_status = topic_starter + "info/status"
topic_warning = topic_starter + "info/warning"
topic_battvolts = topic_starter + "info/battvolts"
topic_joyYL = topic_starter + "control/joyYL"
topic_joyXL = topic_starter + "control/joyXL"
topic_joyYR = topic_starter + "control/joyYR"
topic_joyXR = topic_starter + "control/joyXR"
topic_stopwatch = "stopwatch"

# --- Message handler that processes received MQTT messages ----
def message_handler(client, topic, message):
    global stopwatch_running, stopwatch_seconds, next_clock_tick, stopwatch_start_time

    """
    Method called when a client's subscribed feed has a new value.
    :param str topic: The topic of the feed with a new value.
    :param str message: The new value
    """

    if topic == topic_status:
        temp = message.split(":")
        if len(temp) > 1:
            mode = temp[0]
            status = temp[1]
            if len(mode) > 12:
                splitmode = mode.split(" ")
                mode1_text.text = splitmode[0]
                mode2_text.text = splitmode[1]
            else:
                mode1_text.text = mode[0:11]
                mode2_text.text = mode[11:22]
            status_text.text = status[0:22]
            status_text.color = color=colors.TFT_BLUE
        elif len(temp) == 1:
            status_text.text = message[0:22]
            status_text.color = color=colors.TFT_BLUE

    elif topic == topic_warning:
        status_text.text = message[0:22]
        status_text.color = color=colors.TFT_RED

    elif topic == topic_stopwatch + "/start":
        status_text.text = config.challenge_started_message
        status_text.color = colors.TFT_PASTEL_GREEN
        stopwatch_seconds = 0
        stopwatch_running = True
        stopwatch_start_time = time.monotonic()
        next_clock_tick = time.monotonic() + 1.0

    elif topic == topic_stopwatch + "/stop":
        stopwatch_running = False
        display_banners(statustext = config.challenge_done_message)

    elif topic == topic_stopwatch + "/clear":
        stopwatch_seconds = 0
        display_time(stopwatch_seconds, color=colors.TFT_WHITE)
        display_banners(statustext = config.waiting_to_start_message)

    if config.want_specialty_cmds:
        if topic == topic_joyYL:
            status_text.text = "Manually Driving"
            status_text.color = color=colors.TFT_PURPLE

        elif topic == topic_joyXL:
            status_text.text = "Manually Driving"
            status_text.color = color=colors.TFT_PURPLE

        elif topic == topic_joyYR:
            status_text.text = "Manually Driving"
            status_text.color = color=colors.TFT_PURPLE

        elif topic == topic_joyXR:
            status_text.text = "Manually Driving"
            status_text.color = color=colors.TFT_PURPLE

    if topic == topic_battvolts:
        if stopwatch_running:
            temp = message.split(" ")
            if len(temp) > 0:
                status_text.text = "Battery: " + temp[0] + " v"
                status_text.color = color=colors.TFT_GREEN

def display_time(curtime, color):
    minutes = int(curtime / 60)
    seconds = int(curtime - (60 * minutes))
    clock_text.text = "{minutes}{colon}{seconds:02d}".format(
        minutes=minutes, seconds=seconds, colon=":"
    )
    clock_text.color = color

def display_banners(statustext = config.waiting_to_start_message):
    status_text.text = statustext
    status_text.color = color=colors.TFT_PASTEL_GREEN
    mode1_text.text = config.welcome_banner_1
    mode1_text.color = color=colors.TFT_ORANGE
    mode2_text.text = config.welcome_banner_2
    mode2_text.color = color=colors.TFT_ORANGE


# --- MQTT interface communicator
globals.communicator = Communicator(matrixportal, message_handler)
globals.communicator.subscribe(topic_status)
globals.communicator.subscribe(topic_warning)
globals.communicator.subscribe(topic_joyYL)
globals.communicator.subscribe(topic_joyXL)
globals.communicator.subscribe(topic_joyYR)
globals.communicator.subscribe(topic_joyXR)
globals.communicator.subscribe(topic_stopwatch + "/#")

if (config.want_battery_message):
    globals.communicator.subscribe(topic_battvolts)

stopwatch_running = False
stopwatch_seconds = 0
stopwatch_start_time = time.monotonic()

display_banners(statustext = config.waiting_to_start_message)
next_clock_tick = time.monotonic() + 1.0

while True:
    globals.communicator.client.loop(timeout=0.3)   # (was 0.2)

    if (time.monotonic() > next_clock_tick):

        """
        note: very important, do not just increment the running total counter here!
        it is possible (likely) that some ticks will be missed when the device
        is busy, and the stopwatch will run "slow".  instead, read the processor's
        time.monotonic() value when the timer is started, then calculate the actual
        time elapsed at each tick here.
        """

        if stopwatch_running:
            # stopwatch_seconds = stopwatch_seconds + 1
            stopwatch_seconds = time.monotonic() - stopwatch_start_time

        color = colors.TFT_WHITE
        if (stopwatch_seconds > config.warning_time):
            color = colors.TFT_DARK_ORANGE
        if (stopwatch_seconds > config.too_long_time):
            color = colors.TFT_RED

        display_time(stopwatch_seconds, color)
        next_clock_tick = time.monotonic() + 1.0

    time.sleep(0.100)


