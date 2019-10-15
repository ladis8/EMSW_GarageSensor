"""
\file       webserver.py
\author     Ladislav Stefka
\brief      Classes and methods for deploying web pages and handling requests from browser 
\copyright  none
"""

import cherrypy
import os
import logging
import json
import datetime


#WEB SERVER SETTINGS
ADDRESS = "0.0.0.0"
PORT = 8089
MEDIA_DIR = os.path.join(os.path.abspath("."), u"web")


class Root:
    """Class representing API that can be requested by GET"""

    @cherrypy.config(**{'tools.auth_basic.on': False})
    def OPTIONS(self,**kwargs):
        pass

class Data:
    """Class representing API that can be requested by GET"""

    exposed = True

    def __init__(self, get_status_method):
        self.get_status_callback = get_status_method


    @cherrypy.config(**{'tools.json_in.force': False})
    def GET(self, **kwargs):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        state = self.get_status_callback()
        date = datetime.datetime.now().replace(microsecond=0)
        logging.debug("GET called : state {} asked".format(state))
        return (json.dumps({"humanStatus": state, "timeStamp": str(date)})).encode()



class WebPage:
    """Class representing the web app domain"""

    def __init__(self, ws):
        self.web_server = ws

    @cherrypy.expose
    def app(self):
        """Main app domain, deploys the index.html web page."""

        cherrypy.response.headers['Content-Type'] = "text/html"
        logging.debug("MEDIA directory folder: %s", MEDIA_DIR)
        return open(os.path.join(MEDIA_DIR, u'index.html'))

    @cherrypy.expose
    def index(self):
        """Index domain, tests the cherrypy functionality."""

        cherrypy.response.headers['Content-Type'] = "text/html"
        return "Cherrypy index page call"


    @cherrypy.expose
    def snapshot(self):
        """One frame snapshot, tests the camera functionality."""

        cherrypy.response.headers['Content-Type'] = 'image/jpeg'

        logging.debug("SNAPSHOT CLICKED...")
        # cherrypy.response.headers['X-Timestamp'] = '%f' % (time.time())

        ch = self.web_server.camera_handler
        #START CAMERA
        if not ch.active:
            ch.start_camera()
            ch.set_frame_size()
        #SNAP A FRAME
        if not ch.saving:
            ch.snap_frame()
        frame = ch.get_frame()
        #CONVERT FRAME TO IMAGE AND RETURN IT
        img_data = ch.convert_to_image(frame, base64_encode=False)

        cherrypy.response.headers['Content-Length'] = '%d' % (len(img_data))
        return img_data

    @cherrypy.expose
    def stream(self):
        """MJPEG stream that periodically sends camera capture to web."""

        cherrypy.response.headers['Content-Type'] = "multipart/x-mixed-replace;boundary=--frame"
        WebServer.streaming = True
        return self.content()

    stream._cp_config = {'response.stream': True}


    def content(self):

        while WebServer.streaming:

            #TIME DELAY
            #time.sleep(0.1)
            frame = self.web_server.camera_handler.get_frame()
            if frame is None:
                continue
            img_data = self.web_server.camera_handler.convert_to_image(frame)

            #YIELDING THE MJPEG FRAME
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + img_data + b"\r\n")


class WebServer(object):

    """Class that represents the web server """

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

        #MOUNT
        data = Root()
        data.exposed = True
        data.HumanStatus = Data(get_status_method)
        cherrypy.tools.cors = cherrypy.Tool('before_finalize', WebServer.cors)
        cherrypy.tree.mount(data, '/data', config=api_conf)
        cherrypy.tree.mount(WebPage(self), '/', config=app_conf)

        #DISABLE CHERRYPY LOG
        logger = cherrypy.log.access_log
        logger.removeHandler(logger.handlers[0])
        cherrypy.log.screen = None
        cherrypy.log.access_file = None



    def start(self,address, port=8080):

        cherrypy.config.update({
            'server.socket_host': address,
            'server.socket_port': port
        })
        cherrypy.engine.start()

    def stop(self):
        cherrypy.engine.stop()




