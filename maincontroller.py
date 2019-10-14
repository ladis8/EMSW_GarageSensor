import time
import threading
import logging
import datetime as dt

import tools

from videochunk import VideoChunk
from rpiboard import RpiBoard

class MainController():

    SEND_EMAIL = True

    def __init__(self, ch, vh):
        self.lock = threading.Lock()

        self.STATE = "UNNOTIFIED"
        self.rpi_board = None

        #ASSIGN HANDLERS
        self.camera_handler = ch
        self.video_handler = vh

        #INIT THREAD
        self.controller_thread = threading.Thread(target=self.worker)
        self.is_running = False

        #ASSIGN EVENT LISTENER
        self.rpi_board = RpiBoard()
        self.register_as_observer()

    #OBSERVER PATTERN METHODS

    def __call__(self):
        self.update()

    def register_as_observer(self):
        self.rpi_board.add_observer(self)

    def update(self):
        logging.debug("Main controller notified...")
        #TODO: cases when notified when detected??
        self.lock.acquire()
        self.STATE = "NOTIFIED" if not self.STATE == "DETECTED" else "DETECTED"
        self.lock.release()

    #THREAD METHODS

    def start(self):
        logging.info("Controller started...")
        self.is_running = True
        self.controller_thread.start()

    def stop(self):
        logging.info("Controller stopped...")
        self.rpi_board.clear()
        self.is_running = False
        self.controller_thread.join(0.1)


    def worker(self):

        new_video_chunk = None

        while self.is_running:

            date = dt.datetime.now().replace(microsecond=0)
            logging.debug("{}: Main controller is running...".format(date))
            self.lock.acquire()
            state = self.STATE
            self.lock.release()
            if state == "UNNOTIFIED":
                time.sleep(3)

            elif state == "NOTIFIED":
                #TURN ON THE CAMERA AND SNAP THE IMAGE
                self.camera_handler.start_camera()
                self.camera_handler.set_frame_size()

                self.camera_handler.snap_frame()
                human_detected = self.camera_handler.check_human()


                if not human_detected:
                    logging.warning("EVENT {}: Motion sensor trigerred, human NOT detected".format(date))
                    self.STATE = "UNNOTIFIED"
                    self.camera_handler.close_camera()

                else:
                    logging.warning("EVENT {}: Motion sensor trigerred, human DETECTED".format(date))
                    self.STATE = "DETECTED"

                    #TURN ON LED
                    self.rpi_board.set_led(True)

                    #SEND NOTIFICATION
                    if MainController.SEND_EMAIL:
                        tools.send_notification_email(str(date))

                    #START RECORDING VIDEO
                    #TODO: implement video handelr - saving
                    new_video_chunk = VideoChunk()
                    new_video_chunk.set_start_time(date)
                    new_video_chunk.set_recording()
                    self.camera_handler.set_saving(True)


            elif state == "DETECTED":
                logging.debug("Getting frame...")
                self.camera_handler.snap_frame(detect=False)
                frame = self.camera_handler.get_frame()

                if new_video_chunk.is_within_timedelta(date):
                    new_video_chunk.add_frame_to_data(frame)
                else:
                    logging.info("File {} saved...".format(new_video_chunk.name))
                    self.STATE = "UNNOTIFIED"

                    #TURN OFF LED
                    self.rpi_board.set_led(False)

                    #SAVE VIDEO FILE
                    new_video_chunk.save()
                    self.camera_handler.set_saving(False)

                    #CLOSE CAMERA
                    self.camera_handler.close_camera()

            time.sleep(0.1)


    def get_detection_state(self):
        return self.STATE == "DETECTED"










