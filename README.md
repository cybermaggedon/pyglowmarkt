
# pyglowmarkt

## Introduction

Python API to the Bright/Glowmarkt/Hildebrand API for energy consumption.
There is a python API and a command-line script.

## Install

```
pip3 install pyglowmarkt
```

## API example usage

### Connect

You need an account from https://glowmarkt.com/

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
period = "PT1H"

# Round times to start of period boundary
t_from = resource.round(t_from, period)
t_to = resource.round(t_to, period)

rdgs = resource.get_readings(t_from, t_to, period)
for r in rdgs:
    print("    %s: %s" % (
        r[0].astimezone().replace(tzinfo=None),
        r[1]
    ))
```

Timezones are managed according to t_from and t_to.  If you want to use GMT
timezone, make sure t_from and t_to are set to use that timezone.

### Tariff

```
t = res.get_tariff()
print("    Tariff: rate=%.1f standing=%.1f" % (
    t.current_rates.rate,
    t.current_rates.standing_charge,
))
```

### Not implemented / tested

The API provides the means to get the current value of a resource (the last
data point acquired) and the meter reading (the cumulative value, the number
you would see if you go and look at the meter.

I can't get these to work, maybe not implemented, or maybe only work with
Glowmarkt hardware (I'm testing with a SMETS2 meter).

I don't have a gas smart meter, maybe it would work, maybe not.

## Command line

### `glowmarkt-dump`

Accesses the bright account and dumps out each resource's readings, and
tariff information, human readable.

```
usage: glowmarkt-dump [-h] --username USERNAME --password PASSWORD
                      [--minutes MINUTES] [--period PERIOD]

optional arguments:
  -h, --help            show this help message and exit
  --username USERNAME, -u USERNAME
                        Bright account username
  --password PASSWORD, -p PASSWORD
                        Bright account password
  --minutes MINUTES, -m MINUTES
                        Number of minutes to look back
  --period PERIOD, -d PERIOD
                        Summary period (default: PT1H)
```

e.g.

```
$ glowmarkt-dump -u 'username@example.org' -p 'p4ssw0rd' -m 240 -d PT1H
Entity: DCC Sourced
  electricity consumption:
    2021-06-28 16:00:00: 0.000000 kWh
    2021-06-28 17:00:00: 0.506000 kWh
    2021-06-28 18:00:00: 2.355000 kWh
    2021-06-28 19:00:00: 0.282000 kWh
    2021-06-28 20:00:00: 0.000000 kWh
    current: Not implemented.
    meter reading: Not implemented.
    Tariff: rate=16.3 standing=28.8
  electricity cost:
    2021-06-28 16:00:00: 0.000000 p
    2021-06-28 17:00:00: 8.257920 p
    2021-06-28 18:00:00: 38.433600 p
    2021-06-28 19:00:00: 4.602240 p
    2021-06-28 20:00:00: 0.000000 p
    current: Not implemented.
    meter reading: Not implemented.
    Tariff: rate=16.3 standing=28.8
```

### `glowmarkt-csv`

Accesses the readings for all resources with a particular classifier
and writes out readings in CSV format.  Would be used with e.g.
- `electricity.consumption`
- `electricity.consumption.cost`
- `gas.consumption`
- `gas.consumption.cost`

```
usage: glowmarkt-csv [-h] --username USERNAME --password PASSWORD
                     [--classifier CLASSIFIER] [--minutes MINUTES]
                     [--period PERIOD] [--no-header]

optional arguments:
  -h, --help            show this help message and exit
  --username USERNAME, -u USERNAME
                        Bright account username
  --password PASSWORD, -p PASSWORD
                        Bright account password
  --classifier CLASSIFIER, -c CLASSIFIER
                        Resource classifier to use (default:
                        electricity.consumption)
  --minutes MINUTES, -m MINUTES
                        Number of minutes to look back
  --period PERIOD, -d PERIOD
                        Summary period (default: PT1H)
  --no-header, -n       Suppress CSV header
```

e.g.

```
$ scripts/glowmarkt-csv  -u 'username@example.org' -p 'p4ssw0rd' \
    -m 240 -d PT30M -c electricity.consumption.cost
entity,resource,time,value,unit
DCC Sourced,121d3e6d-ccea-4b46-8b37-798d5cd880b3,2021-06-29T06:30:00,2.59488,pence
DCC Sourced,121d3e6d-ccea-4b46-8b37-798d5cd880b3,2021-06-29T07:00:00,1.82784,pence
DCC Sourced,121d3e6d-ccea-4b46-8b37-798d5cd880b3,2021-06-29T07:30:00,2.1216,pence
DCC Sourced,121d3e6d-ccea-4b46-8b37-798d5cd880b3,2021-06-29T08:00:00,2.31744,pence
DCC Sourced,121d3e6d-ccea-4b46-8b37-798d5cd880b3,2021-06-29T08:30:00,11.21184,pence
DCC Sourced,121d3e6d-ccea-4b46-8b37-798d5cd880b3,2021-06-29T09:00:00,3.1008,pence
DCC Sourced,121d3e6d-ccea-4b46-8b37-798d5cd880b3,2021-06-29T09:30:00,0,pence
DCC Sourced,121d3e6d-ccea-4b46-8b37-798d5cd880b3,2021-06-29T10:00:00,0,pence
```

### `glowmarkt-today`

Shows cumulative consumption for today (since midnight local time).

Accesses the readings for all resources with a particular classifier
and writes out readings in CSV format.  Would be used with e.g.
- `electricity.consumption`
- `electricity.consumption.cost`
- `gas.consumption`
- `gas.consumption.cost`

```
usage: glowmarkt-today [-h] --username USERNAME --password PASSWORD
                       [--classifier CLASSIFIER]

optional arguments:
  -h, --help            show this help message and exit
  --username USERNAME, -u USERNAME
                        Bright account username
  --password PASSWORD, -p PASSWORD
                        Bright account password
  --classifier CLASSIFIER, -c CLASSIFIER
                        Resource classifier to use (default:
                        electricity.consumption)
```

e.g.

```
$ scripts/glowmarkt-today  -u 'username@example.org' -p 'p4ssw0rd' \
    -c electricity.consumption
3.998
```
