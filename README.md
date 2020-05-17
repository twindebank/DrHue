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
