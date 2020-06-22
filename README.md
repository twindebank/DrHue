# DrHue

---

**DrHue** is a package for managing home automation, in the very early stages of development. 

It is capable of managing rules for Philips Hue lights and sensors, and will be extended to integrate other devices too.

See how to use this code in the [example](example) directory.

Run on Pi using:
```bash
# start
make run

# check running
make list

# attach to running session (exit with ctrl+a then ctrl+d)
make attach
```


---





### ToDo

refactor with cloud IoT




---
1. Refactor to decouple some areas of code and how state is shared:
- Adapter/bridge code: should be responsible only for interfacing with bridge:
    * fetching data given a device identifier
    * device identifiers should be formalised in this code (type.name)
    * state that needs to be stored:
        * (in memory) connection
        * (in db) staged changes
        * (in memory) cache of data from bridge, only read once per loop (eventually use to not resend commands to bridge)
        * (in db) states of all registered devices
    * exposed methods:
        * read(uid, property)
        * commit(uid, property, value)
        * push()
        * pull()
- Entity code:
    * friendly abstractions for interacting with devices/groups of devices
    * provides framework to write rules
    * stores state:
        - (in db) active timeout
        - does not store device state, always get that from bridge/adapter

- Runner code:
    * syncing between 
    
- Server code:
    


1. Improve rules and make more tolerant to external changes.
1. Allow setting of sensitivity (motion/brightness)
1. Think about control from webui, maybe rethink how state is stored and communicated between processed (add a [queue](https://stackoverflow.com/questions/24500768/parallel-processing-threading-in-python/24501437#24501437)?)
1. Finish test suite.
1. Add history to entities and helper functions to access history.
1. Simplify rule classes and hide details.
1. Split up example out of repo.
1. Put onto pypi.
1. Integrate with google devices.
1. Data export to bigquery, eventually gather enough data to apply ML.
    * could export all hue bridge data to raw event then build some staging & entity data models
    * would need to send off events from drhue 
1. CI/CD.
