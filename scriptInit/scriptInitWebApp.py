import os, os.path
import random
import string
import cherrypy

class DemoInit(object):
    @cherrypy.expose
    def index(self):
        return open('index.html')

    @cherrypy.expose
    def generateDVS(self):
        return 'went to DVS page'

# CSS http://scache.vzw.com/globalnav/css/globalnav-js.cbfdb61acd.css
    

if __name__ == '__main__':
    
    webapp = DemoInit()
    conf = {
         '/': {
             'tools.sessions.on': True,
             'tools.staticdir.root': os.path.abspath(os.getcwd())
         },
         '/generator': {
             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Content-Type', 'text/plain')],
         },
         '/static': {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': './public'
         }
    }
    cherrypy.config.update({'server.socket_port': 10005})
    cherrypy.quickstart(webapp, '/', conf)