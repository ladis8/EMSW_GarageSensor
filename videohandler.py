import cv2


class VideoHandler:

    video_writer = None
    current_chunk = None



    @staticmethod
    def set_video_chunk(video_chunk):
        current_chunk = video_chunk

        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        video_writer = cv2.VideoWriter(current_chunk.name, fourcc, 20.0, (640, 480))

