import os
from Cheetah.Template import Template
import cherrypy
import hashlib, uuid


salt = uuid.uuid4().hex
password = 'test_password'

hashed_password = hashlib.sha512(password + salt).hexdigest() #то что хранится на сервере

auth_status = False

incoming_password = 'test_password' #то что пишет клиент



def check_pass(incoming_password, hashed_password, salt):
	if (hashlib.sha512(incoming_password + salt).hexdigest() == hashed_password):
		auth_status = True
	else: auth_status = False
	#return auth_status
	print auth_status, hashed_password


check_pass(incoming_password, hashed_password, salt)