#!/usr/bin/env python

from contextlib import suppress
from os import environ

from rtmilk import AuthorizationSession

try:
	from dotenv import load_dotenv
	load_dotenv()
	print('.env imported')
except ImportError:
	pass

def Authorize():
	authenticationSession = AuthorizationSession(environ['RTM_API_KEY'], environ['RTM_SHARED_SECRET'], 'delete')
	print(f'Go to {authenticationSession.url} and authorize')
	with suppress(ImportError):
		from pyperclip import copy
		copy(authenticationSession.url)
		print('URL copied to clipboard')
	input("Press ENTER when you've authorized the app")
	token = authenticationSession.Done()
	filename = 'rtm-token.txt'
	with open(filename, 'w', encoding='utf-8') as f:
		f.write(token)
	print(f'Authorization token written to {filename}')

if __name__ == '__main__':
	Authorize()
