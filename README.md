# DrHue

---

**DrHue** is a package for managing home automation, in the very early stages of development. 

It is capable of managing rules for Philips Hue lights and sensors, and will be extended to integrate other devices too.

See how to use this code in the [example](example) directory.

Run on Pi using:
```bash
# start
screen -dmS drhue python -m example.main

# check running
screen -list

# open session (exit with ctrl+d)
screen -d -r drhue
```


---

### ToDo

1. Fix hotloading code.
1. Figure out better deployment pipeline to Pi, maybe git pull every 20 loops and hot reload code?
1. Add history to entities.
1. Finish test suite.
1. Simplify rule classes and hide details.
1. Build more tolerance for other changes to state eg. from Hue app.
1. Split up example out of repo.
1. Put onto pypi.
1. Integrate with google devices.
1. Data export to bigquery, eventually gather enough data to apply ML.
1. CI/CD.
