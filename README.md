# rtmilk
Python wrapper for "Remember the Milk" [API](https://www.rememberthemilk.com/services/api/)

# Idea
Idea is to use pydantic to (de)structure the requests and responses
There is a raw api wrapper called API which handles authorization, wrapping each call in a function and removing common fields
There will be a higher level wrapper which will have objects representing the implicit objects in the API

# Authorization layer
Stores the key, secret etc
Generates the api sig
Makes generic authorized/unauthorized calls. Inputs are able to be coerced to strings. Outputs are dictionaries that come out of the json parsing

# Wrappers for the specific RTM calls
Inputs are proper types like datetime, enums, lists
Outputs are parsed out into the same types (datetime, enums, lists etc)
Should it throw RTM errors rather than return parsed fail objects? Probably, since it's possible with complete fidelity and fits with the way the code has to be written

# Object layer
The idea is mainly to have an object for a task
This should take care of the ordering of setting start/due dates
Takes care of has_due_time etc

# Client layer
Somehow you have to make it look reasonable from the outside and hide the API details?

# Future?
Make it sansio, so that we can use other than requests
