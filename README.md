
# pyglowmarkt

## Introduction

Python API to the Bright/Glowmarkt/Hildebrand API for energy consumption.
There is a python API and a command-line script.

## API example usage

### Connect

```
from glowmarkt import *

cli = BrightClient("myusername@example.org", "MyP4ssword!")

```

### Discover virtual entities and resources

A virtual entity is e.g. your Glowmarkt device or SMETS2 smart meter.
A virtual entity has multiple resource e.g.
- Electricity consumption
- Electricity cost
- Gas consumption
- Gas cost

```
ents = cli.get_virtual_entities()

for ent in ents:
    print("Entity:", ent.name)
    for res in ent.get_resources():
        print("  %s:" % res.name)
```

### Meter readings over a period of time

Assuming we've got a resource from the discovery above...

`get_readings` returns a list. Each element of the list is a
`[timestamp, value]` pair which will be a `KWH` or `Pence` object.
Use `value.value` to fetch the floating point value, or `str(value)` to
represent as a string with the kWh/pence unit.
```

# Get time now, and 4 hours ago, this is the reading window
now = datetime.datetime.now()
t_from = now - datetime.timedelta(hours=4)
t_to = now

# Results will be summarised at one hour readings
period = PT1H

rdgs = resource.get_readings(t_from, t_to, period)
for r in rdgs:
    print("    %s: %s" % (
        r[0].astimezone().replace(tzinfo=None),
        r[1]
    ))
```

### Not implemented / tested

The API provides the means to get the current value of a resource (the last
data point acquired) and the meter reading (the cumulative value, the number
you would see if you go and look at the meter.

I can't get these to work, maybe not implemented, or maybe only work with
Glowmarkt hardware (I'm testing with a SMETS2 meter).

I don't have a gas smart meter, maybe it would work, maybe not.




