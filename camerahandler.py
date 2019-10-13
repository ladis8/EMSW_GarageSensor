import cv2
import numpy as np
import datetime

from imutils.object_detection import non_max_suppression
from imutils import paths

import base64


# TODO: place timestamp to right corner
class CameraHandler:
    TEXT_POSITION = (50, 50)
    SHOWING_IMAGE = True

    DEFAULT_FRAME_HEIGHT = 480
    DEFAULT_FRAME_WIDTH = 640

    def __init__(self):

        self.camera = None
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

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width);
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height);

    def set_saving(self, saving):
        self.saving = saving

    def start_camera(self):
        self.camera = cv2.VideoCapture(0)

    def close_camera(self):
        self.camera.close()


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

    def snap_frame(self):

        ret, frame = self.camera.read()
        if not ret:
            raise Exception("Camera did not captured the image correctly...")
        # Our operations on the frame come here
        # tuple (480,640) ndarray

        # MAKE IMAGE GREY
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # ADD TIMESTAMP TO IMAGE
        date = datetime.datetime.now().replace(microsecond=0)
        cv2.putText(grey, str(date), CameraHandler.TEXT_POSITION, cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))

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

    def convert_to_image(self, frame):

        # tuple (85010, 1) ndarray --> data reduction
        img_buf_arr = cv2.imencode(".jpeg", frame)[1]
        # img_data = "data:image/jpg;base64," + base64.b64encode(im_buf_arr)
        return bytearray(img_buf_arr)
        #  jpg_as_text = base64.b64encode(str(im_buf_arr))
        # self.camera.release()
        # return str(jpg_as_text)

