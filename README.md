[![codecov](https://codecov.io/gh/rkhwaja/rtmilk/branch/master/graph/badge.svg?token=RaMYgorajr)](https://codecov.io/gh/rkhwaja/rtmilk) [![PyPI version](https://badge.fury.io/py/rtmilk.svg)](https://badge.fury.io/py/rtmilk)

Python wrapper for "Remember the Milk" [API](https://www.rememberthemilk.com/services/api/)

# Usage of client
```python
from rtmilk import Client, RTMError

# These are the equivalent objects, created differently
client = Client.Create(API_KEY, SHARED_SECRET, TOKEN)
client2 = await Client.CreateAsync(API_KEY, SHARED_SECRET, TOKEN)

try:
    task = client.Add(title='title 1')
    assert task.complete.value is False
    task.tags.Set(['tag1', 'tag2'])
    assert task.tags.value == ['tag1', 'tag2']
    task = await client.AddAsync(title='title 2')
    await task.tags.Set(['tag1', 'tag2'])
    tasks = client2.Get('name:"title 1"')
    assert tasks[0].tags.value == ['tag1', 'tag2']
except RTMError as e:
    print(e)
```

# Usage of API functions directly
```python
from rtmilk import API, RTMError

api = API(API_KEY, SHARED_SECRET, TOKEN)

timeline = api.TimelinesCreate().timeline
try:
    api.TasksAdd(timeline, 'task name')
except RTMError as e:
    print(e)
```

```python
from rtmilk import APIAsync, RTMError

apiAsync = APIAsync(API_KEY, SHARED_SECRET, TOKEN)

timeline = await apiAsync.TimelinesCreate().timeline
try:
    await apiAsync.TasksAdd(timeline, 'task name')
except RTMError as e:
    print(e)
```

# Authorization
```python
from rtmilk import AuthorizationSession

authenticationSession = AuthorizationSession(API_KEY, SHARED_SECRET, 'delete')
input(f"Go to {authenticationSession.url} and authorize. Then Press ENTER")
token = authenticationSession.Done()
print(f'Authorization token is {token}')
```
