import cherrypy
import os
import logging
import time
import json
import datetime

import camerahandler as ch
import maincontroller as mc
import videohandler as vh


#WEB SERVER SETTINGS
ADDRESS = "0.0.0.0"
PORT = 8089
MEDIA_DIR = os.path.join(os.path.abspath("."), u"web")

FRAME_HEIGHT = 640
FRAME_WIDTH = 480

logging.getLogger().setLevel(logging.DEBUG)


#TODO:
#       1) test timer callback
#       2) human detection
#       3) email send
#       4) video ???


class Root:
    _CONNECTION_STRING = ""

class Data:

    exposed = True

    def __init__(self, get_status_method):
        self.get_status_callback = get_status_method

    @cherrypy.config(**{'tools.auth_basic.on': False})
    def OPTIONS(self,**kwargs):
        pass

    @cherrypy.config(**{'tools.json_in.force': False})
    def GET(self, **kwargs):
        print("GET called...")
        cherrypy.response.headers['Content-Type'] = 'application/json'
        state = self.get_status_callback()
        date = datetime.datetime.now().replace(microsecond=0)
        print("DEBUG: state asked", state)
        return (json.dumps({"humanStatus": state, "timeStamp": str(date)})).encode()



class FrontEnd:

    def __init__(self, ws):
        self.web_server = ws

    @cherrypy.expose
    def app(self):
        cherrypy.response.headers['Content-Type'] = "text/html"
        logging.debug("MEDIA directory folder: %s", MEDIA_DIR)
        return open(os.path.join(MEDIA_DIR, u'index.html'))

    @cherrypy.expose
    def index(self):
        cherrypy.response.headers['Content-Type'] = "text/html"
        return "Cherrypy index page call"


    # @cherrypy.expose
    # def humanstatus(self):
    #     cherrypy.response.headers['Content-Type'] = 'application/json'
    #     state = self.get_status_callback()
    #     date = datetime.datetime.now().replace(microsecond=0)
    #     print("DEBUG: state asked", state)
    #     return json.load({"humanStatus": state, "timeStamp": date})



    @cherrypy.expose
    def stream(self):

        cherrypy.response.headers['Content-Type'] = "multipart/x-mixed-replace;boundary=--frame"
        # imageInfo = {}
        # imageInfo['width'] = int(width)
        # imageInfo['height'] = int(height)
        # rate = 30

        WebServer.streaming = True
        return self.content()

    stream._cp_config = {'response.stream': True}

    @cherrypy.expose
    def snapshot(self):

        cherrypy.response.headers['Content-Type'] = 'image/jpeg'

        print("SNAPSHOT CLICKED...")
        # cherrypy.response.headers['X-Timestamp'] = '%f' % (time.time())

        ch = self.web_server.camera_handler
        #START CAMERA
        if not self.web_server.camera_handler.active:
            ch.start_camera()
            ch.set_frame_size()
        #SNAP A FRAME
        ch.snap_frame()
        frame = ch.get_frame()
        #CONVERT FRAME TO IMAGE AND RETURN IT
        img_data = ch.convert_to_image(frame, base64_encode=False)

        cherrypy.response.headers['Content-Length'] = '%d' % (len(img_data))
        return img_data


    def content(self, rate=30.0):

        #imageInfoStr = json.dumps(imageInfo)

        while WebServer.streaming:

            #TIME DELAY
            time.sleep(0.1)

            frame = self.web_server.camera_handler.get_frame()
            if frame is None:
                continue

            img_data = self.web_server.camera_handler.convert_to_image(frame)

            #print("Image streamed...")

            # stream = b"--frame\r\n" + ,"utf-8") + img_data + bytes("\r\n--frame\n\r","utf-8")
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + img_data + b"\r\n")
            # yield stream


class WebServer(object):

    streaming = False

    @staticmethod
    def cors():
        headers = cherrypy.response.headers
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
        headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, Authorization'

    def __init__(self, ch, get_status_method):
        self.camera_handler = ch


        api_conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                # 'tools.response_headers.on': True,
                # 'tools.response_headers.headers': [('Content-Type', 'json')],
            }
        }
        app_conf = {
            '/': {
                'tools.sessions.on': True,
                'tools.response_headers.on': True,
            },
            '/css': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': MEDIA_DIR + "/css"
            },
            '/js': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': MEDIA_DIR + "/js"
            },
            '/img': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': MEDIA_DIR + "/img"
            },
            '/media': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': MEDIA_DIR,
                'tools.staticdir.index': 'index.html',
            },
        }


        data = Root()
        data.exposed = True
        data.HumanStatus = Data(get_status_method)


        cherrypy.tools.cors = cherrypy.Tool('before_finalize', WebServer.cors)
        cherrypy.tree.mount(data, '/data', config=api_conf)
        cherrypy.tree.mount(FrontEnd(self), '/', config=app_conf)

        cherrypy.log.error_log.setLevel(30)


    # stops the web application
    def start(self,address, port=8080):
        cherrypy.config.update({
            'server.socket_host': address,
            'server.socket_port': port
        })
        cherrypy.engine.start()

    def stop(self):
        cherrypy.engine.stop()




def main():

    camera_handler = ch.CameraHandler()

    video_handler = vh.VideoHandler()

    server = controller = None

    try:
        logging.warning("Main controller starting...")
        controller = mc.MainController(camera_handler, video_handler)
        controller.start()

        logging.warning("Server starting...")
        server = WebServer(camera_handler, controller.get_detection_state)
        server.start(ADDRESS, PORT)

    except KeyboardInterrupt:
        WebServer.streaming = False
        camera_handler.close_camera()
        if server:
            server.stop()
        if controller:
            controller.stop()
            controller.join()
        logging.warning("Everything closed...")



if __name__ == '__main__':
    main()

