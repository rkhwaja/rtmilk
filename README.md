[![codecov](https://codecov.io/gh/rkhwaja/rtmilk/branch/master/graph/badge.svg?token=RaMYgorajr)](https://codecov.io/gh/rkhwaja/rtmilk) [![PyPI version](https://badge.fury.io/py/rtmilk.svg)](https://badge.fury.io/py/rtmilk)

Python wrapper for "Remember the Milk" [API](https://www.rememberthemilk.com/services/api/)

# Usage of client
```python
from rtmmilk import Client, RTMError, Task

client = Client(API_KEY, SHARED_SECRET, TOKEN)

try:
    client.Add(Task(title='title', tags=['tag1', 'tag2']))
    await client.AddAsync(Task(title='title', tags=['tag1', 'tag2']))
except RTMError as e:
    print(e)
```

# Usage of API functions directly
```python
from rtmmilk import API, RTMError

api = API(API_KEY, SHARED_SECRET, TOKEN)

timeline = api.TasksCreateTimeline().timeline
try:
    api.TasksAdd(timeline, 'task name')
except RTMError as e:
    print(e)
```

# Authorization
```python
from rtmmilk import AuthorizationSession

authenticationSession = AuthorizationSession(API_KEY, SHARED_SECRET, 'delete')
input(f"Go to {authenticationSession.url} and authorize. Then Press ENTER")
token = authenticationSession.Done()
print(f'Authorization token is {token}')
```
