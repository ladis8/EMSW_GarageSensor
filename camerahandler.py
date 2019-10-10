import cv2
import base64



class CameraHandler:


    def __init__(self):

        self.camera = cv2.VideoCapture(0)
        self.frame_width = 480
        self.frame_height = 640


    def set_frame_size(self, frame_height, frame_width):

        self.frame_height = frame_height
        self.frame_width = frame_width

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width);
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height);

    def set_saving(self, saving):
        self.saving = saving

    def get_frame(self):

        ret, frame = self.camera.read()
        if not ret:
            raise Exception("Camera did not captured the image correctly...")
        # Our operations on the frame come here
        #tuple (480,640) ndarray
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #tuple (85010, 1) ndarray --> data reduction
        img_buf_arr = cv2.imencode(".jpeg", gray)[1]
        #img_data = "data:image/jpg;base64," + base64.b64encode(im_buf_arr)
        return bytearray(img_buf_arr)
        #  jpg_as_text = base64.b64encode(str(im_buf_arr))
        #self.camera.release()
        # return str(jpg_as_text)

    def close_camera (self):
        self.camera.close()
