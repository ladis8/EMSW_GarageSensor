"""
\file       videohandler.py
\author     Ladislav Stefka 
\brief      VideoHandler represents the handler for working with video chunks 
            - loading video chunk locally or creating new one by adding frames from camera
\copyright  none
"""
import cv2

#TODO: IMPLEMENT

class VideoHandler:
    """Class that represents the handler for video chunks and all tasks related to video processing"""

    def __init__(self):

        self.video_writer = None
        self.current_chunk = None
        self.video_reader = None


    def set_chunk_saving(self):
        raise NotImplementedError

    def save_next_frame(self, frame):
        raise NotImplementedError

    def set_chunk_loading(self):
        raise NotImplementedError

    def load_next_frame(self):
        raise NotImplementedError


