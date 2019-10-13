
import RPi.GPIO as GPIO
import logging

class RpiBoard:

    SENSOR_PIN = 17
    LED_PIN = 21

    def __init__(self):
        self._observers = []

        #SET UP MOTION SENSOR AS INPUT
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RpiBoard.SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(RpiBoard.LED_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.add_event_detect(RpiBoard.SENSOR_PIN, GPIO.FALLING, callback=self._motion_detected, bouncetime=500)  # button 3

    def set_led(self, state):
        GPIO.output(RpiBoard.LED_PIN, state)


    def _motion_detected(self, channel):
        logging.debug("Button {} triggered...".format(channel))
        #assure that video is not streamed
        self._notify_observers()

    def _notify_observers(self):
        for observer in self._observers:
            observer()

    def add_observer(self, observer):
        self._observers.append(observer)



