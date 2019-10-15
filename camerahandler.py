"""
\file       camerahandler.py
\author     Ladislav Stefka 
\brief      CameraHandler represents the physical camera and its methods solves the image conversion needs
\copyright  none
"""

import cv2
import datetime
import logging
import base64

from picamera.array import PiRGBArray
from picamera import PiCamera


# TODO: place timestamp to right corner
class CameraHandler:
    """Class that represents the camera and all tasks related to image processing"""
    TEXT_POSITION = (50, 50)
    SHOWING_IMAGE = False

    DEFAULT_FRAME_HEIGHT = 480
    DEFAULT_FRAME_WIDTH = 640

    RASPBERRY_PI = True

    def __init__(self):

        self.camera = None
        self.active = False
        self.frame_width = CameraHandler.DEFAULT_FRAME_WIDTH
        self.frame_height = CameraHandler.DEFAULT_FRAME_HEIGHT

        self.saving = False

        self.last_frame = None

        #FACE CLASSIFIER
        self.classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    def set_frame_size(self, frame_height=DEFAULT_FRAME_HEIGHT, frame_width=DEFAULT_FRAME_WIDTH):

        self.frame_height = frame_height
        self.frame_width = frame_width

        if CameraHandler.RASPBERRY_PI:
            self.camera.resolution = (frame_width, frame_height)
        else:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width);
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height);

    def set_saving(self, saving):
        self.saving = saving

    def start_camera(self):
        if not self.active:
            if CameraHandler.RASPBERRY_PI:
                self.camera = PiCamera()
            else:
                self.camera = cv2.VideoCapture(0)

            self.active = True
        else:
            logging.error("Camera has already been activated")


    def close_camera(self):
        self.camera.close()
        self.active = False


    def _detect_human(self, frame):
        return self.classifier.detectMultiScale(frame, 1.1, 4)

    def check_human(self):
        faces = self._detect_human(self.last_frame)
        return len(faces) != 0

    def snap_frame(self, detect=True):

        logging.debug("Snapping...")

        #SNAP THE FRAME
        if CameraHandler.RASPBERRY_PI:
            raw_capture = PiRGBArray(self.camera, size=(self.frame_width, self.frame_height))
            self.camera.capture(raw_capture, format="bgr")
            frame = raw_capture.array
        else:
            ret, frame = self.camera.read()
            if not ret:
                raise Exception("Camera did not captured the image correctly...")


        # MAKE IMAGE GREY
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # ADD TIMESTAMP TO IMAGE
        date = datetime.datetime.now().replace(microsecond=0)
        cv2.putText(grey, str(date), CameraHandler.TEXT_POSITION, cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))

        if detect:
            detected_faces = self._detect_human(grey)

            for (x, y, w, h) in detected_faces:
                cv2.rectangle(grey, (x, y), (x + w, y + h), (255, 0, 0), 2)

        #RENDER IMAGE IF ALLOWED
        if CameraHandler.SHOWING_IMAGE:
            cv2.imshow("webcam", grey)
            if cv2.waitKey(1) == 27:
                return None

        self.last_frame = grey


    def get_frame(self):
        """Getting the most current snapped frame"""
        return self.last_frame

    def convert_to_image(self, frame, base64_encode=False):
        """Conterts numpy nd array to jpeg image represented by bytes, base64 encoding possible"""
        #NOTE: tuple (85010, 1) ndarray --> data reduction
        img_buf_arr = cv2.imencode(".jpeg", frame)[1]
        if base64_encode:
            img_buf_arr = b"data:image/jpeg;base64," + base64.b64encode(img_buf_arr)
            return img_buf_arr
        return bytes(img_buf_arr)


