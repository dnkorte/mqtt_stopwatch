# MiniRobot Chassis Generator

<h1 align="center">
	<img width="853" src="https://github.com/dnkorte/minirobot_chassis/blob/master/pictures/stopwatch.jpg" alt="picture of stopwatch display"><br>MQTT Stopwatch
</h1>


The display described here provides a stopwatch with included text areas for status messages. It receives commands over MQTT.  The display is built from (2) 32x64 LED matrix displays, giving a total field of 32x128 pixels.  It uses an Adafruit MatrixPortal to drive the panel and to connect to an MQTT broker over wifi to receive commands, and is programmed in CircuitPython.

While the unit was built specifically for the [PiWars 2022](https://piwars.org) challenges, it could be easily used for any competitive event that would benefit from a display of status messages and event timing.  In its role for PiWars, the display snooped on messages sent by the robot to the remote control, though it doesn't really care what the source of the messages is.  The display is a read-only device and does not contribute any messages to the stream.

As built, the total display field is 32x128 pixels, however the panels used can be easily chained in either the horizontal or vertical direction to increase the displayable field size.  Only minor software changes are needed to utilize additional panels in either direction.  Additionally, the panels can be purchased in both smaller and larger dot-pitch configurations to permit flexibility in physical size.

Complete documentation for this project is shown on my [Don's Tech Stuff website](https://donstechstuff.com/mqtt_stopwatch/index.php). 
