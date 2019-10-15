"""
\file       videochunk.py
\author     Ladislav Stefka
\brief      Video chunk class representing a piece of video from camera 
\copyright  none
"""

import datetime
import cv2


class VideoChunk:
    """Class that represents a piece of video - chunk that can be either make from video capture or loaded locally"""

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

    def is_within_timedelta(self):
        return datetime.datetime.now() - self.start_time < VideoChunk.TIMEDELTA

    #TODO: deprecated - should be implemented in video handler
    def set_chunk_saving(self):
        self._create_name()
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_out = cv2.VideoWriter('output.avi', fourcc, 20.0, (128, 128))
        path = "{}/{}.avi".format(VideoChunk.OUTPUT_PATH_DIR, self.name)
        self.data = cv2.VideoWriter(path, fourcc, 20.0, (640, 480))

    #TODO: deprecated - should be implemented in video handler
    def set_chunk_loading(self):
        return NotImplementedError

    def add_frame_to_data(self, frame):
        self.data.write(frame)

    def save_video_chunk(self):
        if not self.data == None:
            self.data.release()

    def load_frame_from_data(self):
        return NotImplementedError

    def close_readed_video_chunk(self):
        return NotImplementedError




