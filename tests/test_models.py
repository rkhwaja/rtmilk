from logging import info

from rtm.models import FailStat, ListsGetListResponse, Response, TestEchoResponse

def test_fail():
	failData = {'rsp':{
				'stat':'fail',
				'err':{
					'code': '112',
					'msg': "Method 'rtm.test.ech' not found"
					}
			}
		}
	response = Response(**failData)
	info(response)
	assert isinstance(response, Response), response
	assert isinstance(response.rsp, FailStat), response

def test_ok():
	okData = {'rsp':{
				'stat':'ok',
				'api_key':'9bb013121e8f3650f350b622a1735442',
				'foo':'bar',
				'format':'json',
				'method':'rtm.test.echo'
			}
		}
	response = Response(**okData)
	info(response)
	assert isinstance(response, Response), response
	assert isinstance(response.rsp, TestEchoResponse), response

def test_lists_getlist():
	data = \
		{'rsp':
			{
			'stat': 'ok',
			'api_key': '9bb013121e8f3650f350b622a1735442',
			'format': 'json',
			'method': 'rtm.lists.getList',
			'lists':
				{'list':
					[
						{
							'id': '100653',
							'name': 'Inbox',
							'deleted': '0',
							'locked': '1',
							'archived': '0',
							'position': '-1',
							'smart': '0'
						}
					]
				}
			}
		}
	response = Response(**data)
	info(response)
	assert isinstance(response, Response), response
	assert isinstance(response.rsp, ListsGetListResponse), response
