# -*- coding: utf-8 -*-

"""
Web интерфейс телефонной книги
"""

import os
import os.path
import hashlib, uuid
from Cheetah.Template import Template
import cherrypy
from cherrypy.lib import sessions, static
import tdcsv
import tdods

localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)

PORT = 8080


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
  def check(self, login='', password=''):
    salt = uuid.uuid4().hex
    users = {'login':hashlib.sha512('pass' + salt).hexdigest()}

    login = login.encode('utf-8')
    password = hashlib.sha512(password.encode('utf-8') + salt).hexdigest()

    if cherrypy.session.get('login', None) == 'login':
      raise cherrypy.HTTPRedirect('/database/')
    else:
      if login == "login" and password == users[login]:
        cherrypy.session['login'] = login
        raise cherrypy.HTTPRedirect('/database/')
      else:
        return "wrong login or password" 

  @cherrypy.expose
  def close_session(self):
    cherrypy.session.pop('login', None)
    raise cherrypy.HTTPRedirect('/')

  @cherrypy.expose
  def index(self, num=None):
    if cherrypy.session.get('login', None) == 'login':
      raise cherrypy.HTTPRedirect('/database/')
    else:
      userForm = Template(file=os.path.join(os.curdir, 'index.tmpl')) 
      return str(userForm)  

  @cherrypy.expose
  def download(self, subdivision='0', collaborator='', number='', telephoneType='0'):
    
    subdivision = int(subdivision)
    telephoneType = int(telephoneType)
    collaborator = collaborator.encode('utf-8')
    number = number.encode('utf-8')

    print (subdivision, telephoneType, collaborator, number)

    tdods.save(telephoneDir, subdivision, collaborator, number, telephoneType)

    #                       ТУТ ВСЕ РАБОТАЕТ
    path = os.path.join(absDir, 'telephonedir.ods')

    res = static.serve_file(path, 'application/x-download', 'attachment', os.path.basename(path))

    return res  

    ##############################################################################################
    
  


  @cherrypy.expose
  def database(self, page='0', subdivision='0', collaborator='', number='', telephoneType='0'):
    page = int(page)
    subdivision = int(subdivision)
    telephoneType = int(telephoneType)
    collaborator = collaborator.encode('utf-8')
    number = number.encode('utf-8')

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

    root = Template(file=os.path.join(os.curdir, 'teldir.tmpl'))
    #root = Template(file=os.path.join(os.curdir, 'index.tmpl'))
    root.page = page
    root.subdivision = subdivision
    root.subdivisions = Root.subdivisions
    root.collaborator = collaborator
    root.number = number
    root.telephoneType = telephoneType
    root.telephoneTypes = Root.telephoneTypes
    root.telephoneDir = filter(lambda telephone: lambdaSubdivision(telephone) and \
                                                 lambdaCollaborator(telephone) and \
                                                 lambdaNumber(telephone) and \
                                                 lambdaTelephoneType(telephone), Root.telephoneDir)
    return str(root)

root = Root()

cherrypy.config.update({
  'log.screen': True,
  'environment': 'production',
  'server.socket_port': PORT,
  'server.threadPool':10,
  'tools.staticfile.on': False,
  'tools.sessions.on': True,
  'tools.sessions.timeout': 60,
})

conf = {
  '/style.css': {
    'tools.staticfile.on': True,
    'tools.staticfile.filename': os.path.join(os.getcwd(), 'style.css'),
  },
}

def run(telephoneDir):
  Root.prepare(telephoneDir)
  cherrypy.tree.mount(root, config=conf)
  #cherrypy.quickstart()
  cherrypy.engine.start()

if __name__ == '__main__':
  import tdods
  os.system("fuser -k {0}/tcp".format(PORT))
  telephoneDir = tdcsv.load()
  run(telephoneDir)
