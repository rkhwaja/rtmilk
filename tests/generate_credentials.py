#!/usr/bin/env python

from contextlib import suppress
from os import environ

from rtm import API, AuthorizationSession, FileStorage

try:
	from dotenv import load_dotenv
	load_dotenv()
	print('.env imported')
except ImportError:
	pass

def Authorize():
	rtm = API(environ['RTM_API_KEY'], environ['RTM_SHARED_SECRET'], FileStorage('rtm-token.json'))
	authenticationSession = AuthorizationSession(rtm, 'delete')
	print(f'Go to {authenticationSession.url} and authorize')
	with suppress(ImportError):
		from pyperclip import copy # pylint: disable=import-outside-toplevel
		copy(authenticationSession.url)
		print('URL copied to clipboard')
	input("Press ENTER when you've authorized the app")
	authenticationSession.Done()
	print('Authorization token written to rtm-token.json')

if __name__ == '__main__':
	Authorize()
