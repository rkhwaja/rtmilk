from logging import info
from pprint import pformat

from rtm import List

def test_get_all_lists(api):
	allLists = api.ListsGetList()
	info(pformat(allLists))
	list0 = List(**allLists['lists']['list'][0])
	info(list0)
