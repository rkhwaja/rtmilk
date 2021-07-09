# rtmilk
Python wrapper for "Remember the Milk" [API](https://www.rememberthemilk.com/services/api/)

# Usage
```python
from rtmmilk import API, FileStorage, RTMError

storage = FileStorage('rtm-token.json')
api = API(API_KEY, SHARED_SECRET, storage)

timeline = api.TasksCreateTimeline().timeline
try:
    api.TasksAdd(timeline, 'task name')
except RTMError as e:
    print(e)
```

# Authorization
```python
from rtmmilk import API, AuthorizationSession, FileStorage

api = API(API_KEY, SHARED_SECRET, FileStorage('rtm-token.json'))
authenticationSession = AuthorizationSession(api, 'delete')
input(f"Go to {authenticationSession.url} and authorize. Then Press ENTER")
token = authenticationSession.Done()
print('Authorization token written to rtm-token.json')
```
