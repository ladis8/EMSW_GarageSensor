import os
import io
import logging
import cherrypy
import time

import camerahandler as ch
import json


#WEB SERVER SETTINGS
ADDRESS = "0.0.0.0"
PORT = 8089
MEDIA_DIR = os.path.join(os.path.abspath("."), u"web")

FRAME_HEIGHT = 640
FRAME_WIDTH = 480



logging.getLogger().setLevel(logging.DEBUG)




#
# class StringGen(object):
#     @cherrypy.expose
#     def index(self):
#         return INDEX_HTML # see below
#
#     @cherrypy.expose
#     def prime(self):
#         # this isn't supposed to be efficient.
#         probe = 1
#         while True:
#             yield "ahoj"



class WebServer(object):

    camera_handler = ch.CameraHandler()
    camera_handler.set_frame_size(FRAME_HEIGHT, FRAME_WIDTH)

    streaming = False



    class Root(object):
        _CONNECTION_STRING = ""

        @cherrypy.config(**{'tools.json_in.force': False})
        def POST(self,**kwargs):
            pass

    class FrontEnd(object):

        @cherrypy.expose
        def app (self):
            logging.debug("MEDIA directory folder: %s", MEDIA_DIR)
            return open(os.path.join(MEDIA_DIR, u'index.html'))

        @cherrypy.expose
        def index (self):
            cherrypy.response.headers['Content-Type'] = "text/html"
            return "<html><head></head><body><h1>Streamer></h1><img src='/cam.mjpg'/></body></html>"

        @cherrypy.expose
        def stream(self, width='320', height='240', rate='30'):

            cherrypy.response.headers['Content-Type'] = "multipart/x-mixed-replace;boundary=--frame"
            imageInfo = {}
            imageInfo['width'] = int(width)
            imageInfo['height'] = int(height)

            rate = 30
            WebServer.streaming = True
            return self.content(imageInfo, float(rate))

        stream._cp_config = {'response.stream': True}

        @cherrypy.expose
        def snapshot(self, width=FRAME_WIDTH, height=FRAME_WIDTH):

            WebServer.camera_handler.set_frame_size(height, width)
            img_data = WebServer.camera_handler.get_frame()

            # if unsubscibe:
            # self.subscribedTopics[imageInfoStr].stop()
            # del self.subscribedTopics[imageInfoStr]

            cherrypy.response.headers['Content-Type'] = 'image/jpeg'
            cherrypy.response.headers['Content-Length'] = '%d' % (len(img_data))
            cherrypy.response.headers['X-Timestamp'] = '%f' % (time.time())

            print(img_data)
            return img_data


        def content(self, imageInfo, rate=30.0):

            #imageInfoStr = json.dumps(imageInfo)

            while WebServer.streaming:
                img_data = WebServer.camera_handler.get_frame()
                print("Image streamed...")

                # cherrypy.response.headers['Content-Type'] = 'image/jpeg'
                # cherrypy.response.headers['Content-Length'] = '%d' % (len(img_data))
                # cherrypy.response.headers['X-Timestamp'] = '%f' % (time.time())
                header = "Content-Type: image/jpeg\r\nContent-Length: {}\r\nX-Timestamp: {}\r\n\r\n"\
                    .format(len(img_data), time.time())

                # stream = b"--frame\r\n" + ,"utf-8") + img_data + bytes("\r\n--frame\n\r","utf-8")
                yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + img_data + b"\r\n")
                # yield stream


    def __init__(self):


        api_conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.response_headers.on': True,
                'tools.response_headers.headers': [('Content-Type', 'text/plain')],

            }
        }
        app_conf = {
            '/': {
                'tools.sessions.on': True,
                'tools.response_headers.on': True,
            },
            # '/css': {
            #     'tools.staticdir.on': True,
            #     'tools.staticdir.dir': MEDIA_DIR+"/css"
            # },
            # '/js': {
            #     'tools.staticdir.on': True,
            #     'tools.staticdir.dir': MEDIA_DIR+"/js"
            # },
            '/images': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': MEDIA_DIR+"/img"
            },
            '/media': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': MEDIA_DIR,
                'tools.staticdir.index': 'index.html',
            },
        }


        data = WebServer.Root()
        data.exposed = True
        cherrypy.tree.mount(WebServer.FrontEnd(), '/', config=app_conf)


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


    try:
        print("server starting...")
        server = WebServer().start(ADDRESS, PORT)
    except KeyboardInterrupt:
        WebServer.streaming = False
        WebServer.camera_handler.close_camera()
        #TODO: close cherrypy
        print("Everything closed...")

if __name__ == '__main__':
    main()

