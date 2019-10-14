import datetime
import cv2



class VideoChunk:

    OUTPUT_PATH_DIR = "videos"

    TIMEDELTA = datetime.timedelta(seconds=30)


    def __init__(self, name="garage_default"):
        self.name = name
        self.file_path = self.data = self.start_time = self.end_time = None

    def set_start_time(self, time):
        self.start_time = time

    def set_end_time(self, time):
        self.end_time = time

    def _create_name(self):
        self.name = "rpi_videochunk_{}".format(str(self.start_time).replace(" ", ""))

    def set_recording(self):
        self._create_name()
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_out = cv2.VideoWriter('output.avi', fourcc, 20.0, (128, 128))
        path = "{}/{}.avi".format(VideoChunk.OUTPUT_PATH_DIR, self.name)
        self.data = cv2.VideoWriter(path, fourcc, 20.0, (640, 480))

    def add_frame_to_data(self, frame):
        self.data.write(frame)

    def is_within_timedelta(self, date):
        return datetime.datetime.now() - self.start_time < VideoChunk.TIMEDELTA

    def save(self):
        if not self.data == None:
           self.data.release()

