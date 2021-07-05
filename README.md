# rtmilk
Python wrapper for "Remember the Milk" [API](https://www.rememberthemilk.com/services/api/)

# Idea
Idea is to use pydantic to (de)structure the requests and responses
There is a raw api wrapper called API which handles authorization, wrapping each call in a function and removing common fields
There will be a higher level wrapper which will have objects representing the implicit objects in the API e.g. Task, TaskSeries, List

# Authorization layer
Stores the key, secret etc
Generates the api sig
Makes generic authorized/unauthorized calls. Inputs are able to be coerced to strings. Outputs are dictionaries that come out of the json parsing

# Wrappers for the specific RTM calls
Inputs are proper types like datetime, enums, lists
Outputs are parsed out into the same types (datetime, enums, lists etc)
Should it throw RTM errors rather than return parsed fail objects? Probably, since it's possible with complete fidelity and fits with the way the code has to be written

# Task objects
Ordering of start/due dates
Hide whether they're dates or datetimes
Hiding of "no tag"/tag type inconsistency
Coalesce sending of different attributes to the server with an explicit call - have to do that for start/due dates anyway
Validate the repeat input values

# List objects
Sometimes you only get the listid back, could hide the expansion of the other attributes

# Filter objects
Construct from string
Construct from logical combination of conditions
Output strings to the server using the pydantic stuff

# Client layer
First entry point
Search for tasks
CRUD for lists
Holds the API object

# Future?
Make it sansio, so that we can use other than requests
