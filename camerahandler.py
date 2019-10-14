import cv2
import numpy as np
import datetime
import logging

from picamera.array import PiRGBArray
from picamera import PiCamera

from imutils.object_detection import non_max_suppression
from imutils import paths

import base64


# TODO: place timestamp to right corner
class CameraHandler:
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

        # self.hog = cv2.HOGDescriptor()
        # self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

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

        # # detect people in the image
        # (rects, weights) = self.hog.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=1.05)
        #
        # # draw the original bounding boxes
        # for (x, y, w, h) in rects:
        #     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        #
        # # apply non-maxima suppression to the bounding boxes using a
        # # fairly large overlap threshold to try to maintain overlapping
        # # boxes that are still people
        # rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
        # pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
        #
        # # draw the final bounding boxes
        # for (xA, yA, xB, yB) in pick:
        #     cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
        #
        # # show some information on the number of bounding boxes
        # # filename = imagePath[imagePath.rfind("/") + 1:]
        # filename = "nofilename"
        # print("[INFO] {}: {} original boxes, {} after suppression".format(
        #     filename, len(rects), len(pick)))

        # Detect faces
        return self.classifier.detectMultiScale(frame, 1.1, 4)
        # Draw rectangle around the faces

    def check_human(self):
        faces = self._detect_human(self.last_frame)
        return len(faces) != 0

    def snap_frame(self,detect=True):

        logging.debug("Snapping...")
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

        # Render iamge
        if CameraHandler.SHOWING_IMAGE:
            cv2.imshow("webcam", grey)
            if cv2.waitKey(1) == 27:
                return None

        self.last_frame = grey

    def get_frame(self):
        return self.last_frame

    def convert_to_image(self, frame, base64_encode=False):

        # tuple (85010, 1) ndarray --> data reduction
        img_buf_arr = cv2.imencode(".jpeg", frame)[1]
        if base64_encode:
            img_buf_arr = b"data:image/jpeg;base64," + base64.b64encode(img_buf_arr)
            return img_buf_arr
        return bytes(img_buf_arr)


