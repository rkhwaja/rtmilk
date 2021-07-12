#!/usr/bin/env python

from contextlib import suppress
from os import environ

from rtmilk import API, AuthorizationSession

try:
	from dotenv import load_dotenv
	load_dotenv()
	print('.env imported')
except ImportError:
	pass

def Authorize():
	rtm = API(environ['RTM_API_KEY'], environ['RTM_SHARED_SECRET'], None)
	authenticationSession = AuthorizationSession(rtm, 'delete')
	print(f'Go to {authenticationSession.url} and authorize')
	with suppress(ImportError):
		from pyperclip import copy # pylint: disable=import-outside-toplevel
		copy(authenticationSession.url)
		print('URL copied to clipboard')
	input("Press ENTER when you've authorized the app")
	token = authenticationSession.Done()
	filename = 'rtm-token.txt'
	with open(filename) as f:
		f.write(token)
	print(f'Authorization token written to {filename}')

if __name__ == '__main__':
	Authorize()
