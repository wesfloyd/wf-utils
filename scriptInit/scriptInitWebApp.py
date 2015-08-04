import os, os.path
import random
import string
import subprocess
from subprocess import call
import cherrypy


#######################################################
# Define custom scripts in the action** functions below
#######################################################

def actionDVS():
    return 'time date'

def actionSearch():
    return 'echo "hello World Search"'

def actionSC():
    return 'echo "hello World SC"'



class DemoInit(object):
    @cherrypy.expose
    def index(self):
        log('WF Debug: in DemoInit get method')
        return open('index.html')

class GenerateService(object):
    exposed = True

    @cherrypy.tools.accept(media='text/plain')
    def GET(self, module):

        if module == 'dvs':
            log('Executing DVS Command')
            executeLocalCommand(actionDVS())
        elif module == 'search':
            log('Executting search command')
            executeLocalCommand(actionSearch())
        elif module == 'sc':
            log('Executing sitecatalyst command')
            executeLocalCommand(actionSC())
        else:
            log('module value ' + module + ' not recognized')


def log(str):
    print "DEBUG: " + str

def executeLocalCommand(cmdVar):
    log('Executing command:' + cmdVar)
    subprocess.call(cmdVar.split(" "))
    # consider modifying the split() method to use Regex - http://stackoverflow.com/questions/1059559/python-split-strings-with-multiple-delimiters


if __name__ == '__main__':
    
    
    conf = {
         '/': {
             'tools.sessions.on': True,
             'tools.staticdir.root': os.path.abspath(os.getcwd())
         },
         '/generate': {
             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Content-Type', 'text/plain')],
         },
         '/static': {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': './public'
         }
    }
    cherrypy.config.update({'server.socket_port': 10005, 'log.screen': False,'server.socket_host': '127.0.0.1'})
    webapp = DemoInit()
    webapp.generate = GenerateService()
    cherrypy.quickstart(webapp, '/', conf)