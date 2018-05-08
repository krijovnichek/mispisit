# -*- coding: utf-8 -*-

"""
Web интерфейс телефонной книги
"""

import os
from Cheetah.Template import Template
import cherrypy
from cherrypy.lib.httputil import parse_query_string
import hashlib, uuid


class Auth:
  @cherrypy.expose
  def index(self):
    auth = Template(file=os.path.join(os.curdir, 'auth.html'))
    return str(auth)

  
class Root:
  @staticmethod
  def prepare(telephoneDir):
    Root.collaborators = list(sorted(telephoneDir.subdivision))
    Root.subdivisions = list(sorted(telephoneDir.subdivision.iterSubdivision()))
    Root.subdivisions.insert(0, 'все')
    Root.telephoneTypes = list(sorted(telephoneDir.telephones.telephoneTypes))
    Root.telephoneTypes.insert(0, 'все')
    Root.telephoneDir = list(sorted(telephoneDir))

  @cherrypy.expose
  def index(self, page='0', subdivision='0', collaborator="", number="", telephoneType='0'):
    page = int(page)
    subdivision = int(subdivision)
    telephoneType = int(telephoneType)

    if not subdivision:
      lambdaSubdivision = lambda rec: True
    else:
      s = Root.subdivisions[subdivision]
      lambdaSubdivision = lambda rec: rec.collaborator in s

    if not collaborator:
      lambdaCollaborator = lambda rec: True
    else:
      l = len(collaborator)
      lambdaCollaborator = lambda rec: str(rec.collaborator)[0:l] == collaborator

    if not number:
      lambdaNumber = lambda rec: True
    else:
      l = len(number)
      lambdaNumber = lambda rec: str(rec.telephone.number)[0:l] == number

    if not telephoneType:
      lambdaTelephoneType = lambda rec: True
    else:
      t = Root.telephoneTypes[telephoneType]
      lambdaTelephoneType = lambda rec: rec.telephone.type == t

    root = Template(file=os.path.join(os.curdir, 'index.tmpl'))
    root.page = page
    root.subdivision = subdivision
    root.subdivisions = Root.subdivisions
    root.collaborator = collaborator.encode('utf-8')
    root.number = number.encode('utf-8')
    root.telephoneType = telephoneType
    root.telephoneTypes = Root.telephoneTypes
    root.telephoneDir = filter(lambda telephone: lambdaSubdivision(telephone) and \
                                                 lambdaCollaborator(telephone) and \
                                                 lambdaNumber(telephone) and \
                                                 lambdaTelephoneType(telephone), Root.telephoneDir)
    if not cherrypy.session.get('name', None):
      raise cherrypy.HTTPRedirect('/auth')
    else:
      return str(root)


    
    
  @cherrypy.expose
  def auth(self):
    auth = Template(file=os.path.join(os.curdir, 'auth.html'))
    return str(auth)
  @cherrypy.expose
  def validate(self,name, password):
    salt = uuid.uuid4().hex
    login = 'login'
    savedpassword = 'password'

    if name == login:
      hashed_password = hashlib.sha512(savedpassword + salt).hexdigest()
      if (hashlib.sha512(password + salt).hexdigest() == hashed_password):
        cherrypy.session['name'] = name
        raise cherrypy.HTTPRedirect('/index')
        auth_status = True 
      else:
        raise cherrypy.HTTPRedirect('/auth')
        auth_status = False
      print auth_status, hashed_password
    else:
      raise cherrypy.HTTPRedirect('/auth')
  @cherrypy.expose
  def logout(self):
    cherrypy.session.pop('name', None)
    raise cherrypy.HTTPRedirect('/auth')

root = Root()
auth = Auth()

# d = cherrypy.dispatch.RoutesDispatcher()
# d.connect('app', '/', controller = root, action = 'index')
# d.connect('app', '/index', controller = root, action = 'index')
# d.connect('auth', '/auth', controller = auth, action = 'index')

cherrypy.config.update({
  'log.screen': True,
  'environment': 'production',
  'server.socket_port': 8085,
  'server.threadPool':10,
  'tools.staticfile.on': False,
  'tools.sessions.on': True,
  'tools.sessions.timeout': 60,
})

conf = {
  # '/': {'request.dispatch': d},
  '/style.css': {
    'tools.staticfile.on': True,
    'tools.staticfile.filename': os.path.join(os.getcwd(), 'style.css'),
  },
}

def run(telephoneDir):
  Root.prepare(telephoneDir)
  cherrypy.tree.mount(root, config=conf)
  cherrypy.quickstart(root,config=conf)

  # try:
  #   cherrypy.engine.start()
  # except cherrypy.NotReady:
  #   cherrypy.server.restart()

if __name__ == '__main__':
  import tdcsv

  os.system("fuser -k 8085/tcp")
  telephoneDir = tdcsv.load()
  run(telephoneDir)
  # print ('___________________________________________________')
  # print(parse_query_string(cherrypy.request.query_string))
  # print ('___________________________________________________')

