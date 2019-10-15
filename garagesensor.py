"""
\file       garagesensor.py
\author     Ladislav Stefka 
\brief      Main script that runs when program is launched - starts web server and main controller, sets logging level 
\copyright  none
"""


import logging

import camerahandler as ch
import maincontroller as mc
import videohandler as vh
import webserver as ws

def main():

    logging.getLogger().setLevel(logging.DEBUG)

    camera_handler = ch.CameraHandler()
    video_handler = vh.VideoHandler()

    server = controller = None

    try:
        logging.warning("Main controller starting...")
        controller = mc.MainController(camera_handler, video_handler)
        controller.start()

        logging.warning("Server starting...")
        server = ws.WebServer(camera_handler, controller.get_detection_state)
        server.start(ws.ADDRESS, ws.PORT)

    except KeyboardInterrupt:
        ws.WebServer.streaming = False
        camera_handler.close_camera()
        if server:
            server.stop()
        if controller:
            controller.stop()
            controller.join()
        logging.warning("Everything closed...")

if __name__ == '__main__':
    main()

