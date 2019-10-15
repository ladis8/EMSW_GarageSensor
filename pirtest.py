"""
\file       pirtest.py
\author     Ladislav Stefka 
\brief      Separate programme used for PIR sensor testing 
\copyright  none
"""

import RPi.GPIO as GPIO
import time

class RpiBoard:

    SENSOR_PIN = 17
    LED_PIN = 21

    def __init__(self):
        self._observers = []

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RpiBoard.SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(RpiBoard.LED_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.add_event_detect(RpiBoard.SENSOR_PIN, GPIO.FALLING, callback=self._motion_detected, bouncetime=500)  # button 3
        while True:
            self.set_led(False)
            time.sleep(0.5)

    def set_led(self, state):
        GPIO.output(RpiBoard.LED_PIN, state)


    def _motion_detected(self, channel):
        print("Button {} triggered...".format(channel))
        self.set_led(True)
        time.sleep(0.5)

try:
    rpi = RpiBoard()
except KeyboardInterrupt:
    GPIO.cleanup()


