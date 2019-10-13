import time
import threading
import datetime as dt

import tools

from videochunk import VideoChunk
from rpiboard import RpiBoard

class MainController():

    def __init__(self, ch, vh):

        self.STATE = "NOTIFIED"
        self.rpi_board = None

        #ASSIGN HANDLERS
        self.camera_handler = ch
        self.video_handler = vh

        #INIT THREAD
        self.controller_thread = threading.Thread(target=self.worker)
        self.is_running = False

        #ASSIGN EVENT LISTENER
        self.rpi_board = RpiBoard()
        self.rpi_board.add_observer(self)

        #activate artificial timer
        # t = threading.Timer(5.0, )





    def __call__(self, param):
        print("Main controller notified...")
        #TODO: cases when notified when detected??
        self.STATE = "NOTIFIED" if not self.STATE == "DETECTED" else "DETECTED"


    def start(self):
        print("Controller started...")
        self.is_running = True
        self.controller_thread.start()

    def stop(self):
        print("Controller stopped...")
        self.is_running = False
        self.controller_thread.join(0.1)


    def worker(self):

        new_video_chunk = None

        while self.is_running:

            date = dt.datetime.now().replace(microsecond=0)
            print("INFO {}: Main controller is running...".format(date))
            if self.STATE == "UNNOTIFIED":
                time.sleep(3)

            elif self.STATE == "NOTIFIED":
                #TURN ON THE CAMERA AND SNAP THE IMAGE
                self.camera_handler.start_camera()
                self.camera_handler.set_frame_size()

                self.camera_handler.snap_frame()
                human_detected = self.camera_handler.check_human()
                #TODO: logging???

                #SEND NOTIFICATION
                #tools.send_notification_email(str(date))

                if not human_detected:
                    print("EVENT {}: Motion sensor trigerred, human NOT detected".format(date))
                    self.STATE = "UNNOTIFIED"
                else:
                    print("EVENT {}: Motion sensor trigerred, human DETECTED".format(date))
                    self.STATE = "DETECTED"


                    #START RECORDING VIDEO
                    #TODO: implement video handelr - saving
                    new_video_chunk = VideoChunk()
                    new_video_chunk.set_start_time(date)
                    new_video_chunk.set_recording()
                    self.camera_handler.set_saving(True)


            elif self.STATE == "DETECTED":
                print("Getting frame...")
                self.camera_handler.snap_frame()
                frame = self.camera_handler.get_frame()

                if new_video_chunk.is_within_timedelta(date):
                    new_video_chunk.add_frame_to_data(frame)
                else:
                    print("File saved...")
                    self.STATE = "UNNOTIFIED"
                    new_video_chunk.save()

            time.sleep(0.1)


    def get_detection_state(self):
        return self.STATE == "DETECTED"










