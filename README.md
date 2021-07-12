Python wrapper for "Remember the Milk" [API](https://www.rememberthemilk.com/services/api/)

# Usage
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
from rtmmilk import API, AuthorizationSession

api = API(API_KEY, SHARED_SECRET, None)
authenticationSession = AuthorizationSession(api, 'delete')
input(f"Go to {authenticationSession.url} and authorize. Then Press ENTER")
token = authenticationSession.Done()
print(f'Authorization token is {token}')
api.SetToken(token)
```
