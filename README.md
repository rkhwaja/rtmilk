[![codecov](https://codecov.io/gh/rkhwaja/rtmilk/branch/master/graph/badge.svg?token=RaMYgorajr)](https://codecov.io/gh/rkhwaja/rtmilk) [![PyPI version](https://badge.fury.io/py/rtmilk.svg)](https://badge.fury.io/py/rtmilk)

Python wrapper for "Remember the Milk" [API](https://www.rememberthemilk.com/services/api/)
- Asynchronous and synchronous APIs
- Subscription support

# Usage of client
```python
from rtmilk.client import Client
from rtmmilk.models import RTMError

# These are the equivalent objects, created differently
client = Client.Create(API_KEY, SHARED_SECRET, TOKEN)
client2 = await Client.CreateAsync(API_KEY, SHARED_SECRET, TOKEN)

try:
    task = client.Add(name='name 1')
    assert task.complete.value is False
    task.tags.Set({'tag1', 'tag2'})
    assert task.tags.value == {'tag1', 'tag2'}
    task = await client.AddAsync(name='name 2')
    await task.tags.SetAsync({'tag1', 'tag2'})
    tasks = client2.Get('name:"name 1"')
    assert tasks[0].tags.value == {'tag1', 'tag2'}
except RTMError as e:
    print(e)
```

# Usage of API functions directly
```python
from rtmilk.api_sync import API
from rtmmilk.models import FailStat

api = API(API_KEY, SHARED_SECRET, TOKEN)

timeline = api.TimelinesCreate().timeline
result = api.TasksAdd(timeline, 'task name')
if isinstance(result, FailStat):
    print(f'Error: {result}')
```

```python
from rtmilk.api_async import APIAsync
from rtmmilk.models import FailStat

apiAsync = APIAsync(API_KEY, SHARED_SECRET, TOKEN)

timeline = await apiAsync.TimelinesCreate().timeline
result = await apiAsync.TasksAdd(timeline, 'task name')
if isinstance(result, FailStat):
    print(f'Error: {result}')
```

# Authorization
```python
from rtmilk.authorization import AuthorizationSession

authenticationSession = AuthorizationSession(API_KEY, SHARED_SECRET, 'delete')
input(f'Go to {authenticationSession.url} and authorize. Then Press ENTER')
token = authenticationSession.Done()
print(f'Authorization token is {token}')
```
