# rtm-python
Python wrapper for "Remember the Milk" [API](https://www.rememberthemilk.com/services/api/)

# Idea
Idea is to use pydantic to (de)structure the requests and responses
There is a raw api wrapper called API which handles authorization, wrapping each call in a function and removing common fields
There will be a higher level wrapper which will have objects representing the implicit objects in the API

# Object layer
The idea is mainly to have an object for a task

# Client layer
Somehow you have to make it look reasonable from the outside and hide the API details?

# Future?
Make it sansio, so that we can use other than requests
