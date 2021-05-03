from logging import info
from pprint import pformat

from rtm import Client, List

def test_get_all_lists(api):
	allLists = api.ListsGetList()
	info(pformat(allLists))
	theList = List(client=Client(api), **allLists['lists']['list'][2])
	info(theList)
	info(f'{theList.name=}')
	theList.name = 'Changed name'
