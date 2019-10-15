"""
\file       rpiboard.py
\author     Jake Hunt 
\brief      RPiBoard represents the physical board
            - handles the GPIO pins and notifies the main controller when the motion event is triggered
\copyright  none
"""

import RPi.GPIO as GPIO
import logging

class RPiBoard:

    SENSOR_PIN = 17
    LED_PIN = 21

    def __init__(self):
        self._observers = []

        GPIO.setmode(GPIO.BCM)
        #SET UP MOTION SENSOR AS INPUT
        GPIO.setup(RPiBoard.SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #SET UP LED AS OUTPUT
        GPIO.setup(RPiBoard.LED_PIN, GPIO.OUT, initial=GPIO.LOW)
        #ASSIGN A CALLBACK ON MOTION SENSOR EDGE
        GPIO.add_event_detect(RPiBoard.SENSOR_PIN, GPIO.FALLING, callback=self._motion_detected, bouncetime=500)  # button 3

    def set_LED(self, state):
        GPIO.output(RPiBoard.LED_PIN, state)

    def _motion_detected(self, channel):
        logging.debug("Button {} triggered...".format(channel))
        #TODO: assure that video is not streamed
        self._notify_observers()

    def _notify_observers(self):
        for observer in self._observers:
            observer()

    def add_observer(self, observer):
        self._observers.append(observer)

    def clear_GPIO(self):
        GPIO.cleanup()



