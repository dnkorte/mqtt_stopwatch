# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Scoreboard matrix display
# uses AdafruitIO to set scores and team names for a scoreboard
# Perfect for cornhole, ping pong, and other games

import time
import board
import terminalio
import displayio
from adafruit_display_text.label import Label
# from adafruit_bitmap_font import bitmap_font
# from adafruit_matrixportal.matrix import Matrix
from adafruit_matrixportal.matrixportal import MatrixPortal

from device_communicator import Communicator
# import message_handler
import colors

# Get global variables
try:
    import globals
except ImportError:
    print("Missing globals.py file")
    raise

# --- MatrixPortal setup ---
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, height=32, width=128, debug=False)

# --- Display setup ---
display = matrixportal.display
group = displayio.Group(max_size=12)  # Create a Group
display.show(group)

font = terminalio.FONT

status_text = Label(font, x=2, y=25, color=colors.TFT_BLUE, max_glyphs=40)
group.append(status_text)
status_text.text = ""

mode1_text = Label(font, x=56, y=5, color=colors.TFT_ORANGE, max_glyphs=40)
group.append(mode1_text)
mode1_text.text = "PiWars 2022"

mode2_text = Label(font, x=56, y=15, color=colors.TFT_ORANGE, max_glyphs=40)
group.append(mode2_text)
mode2_text.text = "Barn Rats"

clock_text = Label(font, x=4, y=9, color=colors.TFT_WHITE, scale=2, max_glyphs=8)
group.append(clock_text)
clock_text.text = "0:00"

# --- display a startup message
status_text.text = "Connecting to Network"
status_text.color = color=colors.TFT_GREEN

# --- MQTT messages setup ----
connected_device = "robot4"
topic_status = connected_device + "/info/status"
topic_warning = connected_device + "/info/warning"
topic_battvolts = connected_device + "/info/battvolts"
topic_joyYL = connected_device + "/control/joyYL"
topic_joyXL = connected_device + "/control/joyXL"
topic_joyYR = connected_device + "/control/joyYR"
topic_joyXR = connected_device + "/control/joyXR"
topic_stopwatch = "stopwatch"

# --- Message handler that processes received MQTT messages ----
def message_handler(client, topic, message):
    global stopwatch_running, stopwatch_seconds, next_clock_tick

    """
    Method called when a client's subscribed feed has a new value.
    :param str topic: The topic of the feed with a new value.
    :param str message: The new value
    """

    if topic == topic_battvolts:
        print("battvolts", message)
        #if stopwatch_running:
        #    temp = message.split(" ")
        #    if len(temp) > 0:
        #        status_text.text = "Battery: " + temp[0] + " v"
        #        status_text.color = color=colors.TFT_GREEN

    elif topic == topic_status:
        print("status", message)
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

    elif topic == topic_warning:
        print("warning", message)
        status_text.text = status[0:22]
        status_text.color = color=colors.TFT_RED

    elif topic == topic_joyYL:
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

    elif topic == topic_stopwatch + "/clear":
        stopwatch_seconds = 0
        display_time(stopwatch_seconds, color=colors.TFT_WHITE)
        display_banners(statustext = "Waiting to Start")

    elif topic == topic_stopwatch + "/start":
        status_text.text = "Challenge Started"
        status_text.color = color=colors.TFT_PASTEL_GREEN
        stopwatch_seconds = 0
        stopwatch_running = True
        next_clock_tick = time.monotonic() + 1.0

    elif topic == topic_stopwatch + "/stop":
        stopwatch_running = False
        display_banners(statustext = "Challenge Done")

def display_time(curtime, color):
    minutes = int(curtime / 60)
    seconds = curtime - (60 * minutes)

    colon = ":"

    clock_text.text = "{minutes}{colon}{seconds:02d}".format(
        minutes=minutes, seconds=seconds, colon=colon
    )
    clock_text.color = color

def display_banners(statustext = "Waiting to Start"):
    status_text.text = statustext
    status_text.color = color=colors.TFT_PASTEL_GREEN
    mode1_text.text = "PiWars 2022"
    mode1_text.color = color=colors.TFT_ORANGE
    mode2_text.text = "Barn Rats"
    mode2_text.color = color=colors.TFT_ORANGE


# --- MQTT interface communicator
globals.communicator = Communicator(matrixportal, message_handler)
globals.communicator.subscribe(topic_status)
# globals.communicator.subscribe(topic_warning)
# globals.communicator.subscribe(topic_battvolts)
globals.communicator.subscribe(topic_joyYL)
globals.communicator.subscribe(topic_joyXL)
globals.communicator.subscribe(topic_joyYR)
globals.communicator.subscribe(topic_joyXR)
globals.communicator.subscribe(topic_stopwatch + "/#")

stopwatch_running = False
stopwatch_seconds = 0
display_banners(statustext = "Waiting to Start")
next_clock_tick = time.monotonic() + 1.0

while True:
    globals.communicator.client.loop(timeout=0.3)   # (was 0.2)

    if (time.monotonic() > next_clock_tick):
        if stopwatch_running:
            stopwatch_seconds = stopwatch_seconds + 1

        color = colors.TFT_WHITE
        if (stopwatch_seconds > 239):
            color = colors.TFT_DARK_ORANGE
        if (stopwatch_seconds > 299):
            color = colors.TFT_RED

        display_time(stopwatch_seconds, color)
        next_clock_tick = time.monotonic() + 1.0

    time.sleep(0.100)



