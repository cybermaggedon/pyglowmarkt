
import requests
import json
import datetime
import time

PT1M = "PT1M"
PT30M = "PT30M"
PT1H = "PT1H"
P1D = "P1D"
P1W = "P1W"
P1M = "P1M"
P1Y = "P1Y"

class Rate:
    pass

class Pence:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "%.2f p" % self.value
    def unit(self):
        return "pence"

class KWH:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "%.3f kWh" % self.value
    def unit(self):
        return "kWh"

class Unknown:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "%s" % self.valu
    def unit(self):
        return "unknown"

class VirtualEntity:
    def get_resources(self):
        return self.client.get_resources(self.id)

class Tariff:
    pass

class Resource:
    def get_readings(self, t_from, t_to, period, func="sum"):
        return self.client.get_readings(self.id, t_from, t_to, period, func)
    def get_current(self):
        return self.client.get_current(self.id)
    def get_meter_reading(self):
        return self.client.get_meter_reading(self.id)
    def get_tariff(self):
        return self.client.get_tariff(self.id)
    def round(self, when, period):
        return self.client.round(when, period)

class BrightClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.application = "b0f1b774-a586-4f72-9edd-27ead8aa7a8d"
        self.url = "https://api.glowmarkt.com/api/v0-1/"
        self.session = requests.Session()

        self.token = self.authenticate()

    def authenticate(self):

        headers = {
            "Content-Type": "application/json",
            "applicationId": self.application
        }

        data = {
            "username": self.username,
            "password": self.password
        }

        url = self.url + "auth"

        resp = self.session.post(url, headers=headers, data=json.dumps(data))

        if resp.status_code != 200:
            raise RuntimeError("Authentication failed")

        resp = resp.json()

        if resp["valid"] == False:
            raise RuntimeError("Expected an authentication token")

        if "token" not in resp:
            raise RuntimeError("Expected an authentication token")

        return resp["token"]

    def get_virtual_entities(self):

        headers = {
            "Content-Type": "application/json",
            "applicationId": self.application,
            "token": self.token
        }

        url = self.url + "virtualentity"

        resp = self.session.get(url, headers=headers)

        if resp.status_code != 200:
            raise RuntimeError("Request failed")

        resp = resp.json()

        ves = []

        for elt in resp:

            ve = VirtualEntity()

            ve.client = self

            ve.application = elt["applicationId"]
            ve.type_id = elt["veTypeId"]
            ve.id = elt["veId"]

            if "postalCode" in elt:
                ve.postal_code = elt["postalCode"]
            else:
                ve.postal_code = None

            if "name" in elt:
                ve.name = elt["name"]
            else:
                ve.name = None

            ves.append(ve)

        return ves

    def get_resources(self, ve):

        headers = {
            "Content-Type": "application/json",
            "applicationId": self.application,
            "token": self.token
        }

        url = self.url + "virtualentity/" + ve + "/resources"

        resp = self.session.get(url, headers=headers)

        if resp.status_code != 200:
            raise RuntimeError("Request failed")

        resp = resp.json()

        resources = []

        for elt in resp["resources"]:
            r = Resource()
            r.id = elt["resourceId"]
            r.type_id = elt["resourceTypeId"]
            r.name = elt["name"]
            r.classifier = elt["classifier"]
            r.description = elt["description"]
            r.base_unit = elt["baseUnit"]

            r.client = self

            resources.append(r)
            
        return resources

    def round(self, when, period):

        # Work out a rounding value.  Readings seem to be more accurate if
        # rounded to the near thing...
        if period == "PT1M":
            when = when.replace(second=0, microsecond=0)
        if period == "PT30M":
            when = when.replace(minute=int(when.minute / 30),
                                second=0,
                                microsecond=0)
        elif period == "PT1H":
            when = when.replace(minute=0,
                                second=0,
                                microsecond=0)
        elif period == "P1D":
            when = when.replace(hour=0, minute=0,
                                second=0,
                                microsecond=0)
        elif period == "P1W":
            when = when.replace(hour=0, minute=0,
                                second=0,
                                microsecond=0)
        elif period == "P1M":
            when = when.replace(day=1, hour=0, minute=0,
                                second=0,
                                microsecond=0)
        else:
            raise RuntimeError("Period %s not known" % period)

        return when

    def get_readings(self, resource, t_from, t_to, period, func="sum"):

        headers = {
            "Content-Type": "application/json",
            "applicationId": self.application,
            "token": self.token
        }

        utc = datetime.timezone.utc

        # Offset in minutes
        offset = -t_from.utcoffset().seconds / 60

        def time_string(x):
            if isinstance(x, datetime.datetime):
                x = x.replace(tzinfo=None)
                return x.isoformat()
            elif isinstance(x, datetime.date):
                x = x.replace(tzinfo=None)
                return x.isoformat()
            else:
                raise RuntimeError("to_from/t_to should be date/datetime")

        t_from = time_string(t_from)
        t_to = time_string(t_to)

        params = {
            "from": t_from,
            "to": t_to,
            "period": period,
            "offset": offset,
            "function": func,
        }

        url = self.url + "resource/" + resource + "/readings"

        resp = self.session.get(url, headers=headers, params=params)

        if resp.status_code != 200:
            raise RuntimeError("Request failed")

        resp = resp.json()

        if resp["units"] == "pence":
            cls = Pence
        elif resp["units"] == "kWh":
            cls = KWH
        else:
            cls = Unknown

        return [
            [datetime.datetime.fromtimestamp(v[0] + 60 * offset).astimezone(),
             cls(v[1])]
            for v in resp["data"]
        ]

    def get_current(self, resource):

        # Tried it against the API, no data is returned
        raise RuntimeError("Not implemented.")

        headers = {
            "Content-Type": "application/json",
            "applicationId": self.application,
            "token": self.token
        }

        utc = datetime.timezone.utc

        url = self.url + "resource/" + resource + "/current"

        resp = self.session.get(url, headers=headers)

        if resp.status_code != 200:
            raise RuntimeError("Request failed")

        resp = resp.json()

        if len(resp["data"]) < 1:
            raise RuntimeError("Current reading not returned")

        if resp["units"] == "pence":
            cls = Pence
        elif resp["units"] == "kWh":
            cls = KWH
        else:
            cls = Unknown

        return [
            [datetime.datetime.fromtimestamp(v[0], tz = utc), cls(v[1])]
            for v in resp["data"]
        ]

    def get_meter_reading(self, resource):

        # Tried it against the API, an error is returned
        raise RuntimeError("Not implemented.")

        headers = {
            "Content-Type": "application/json",
            "applicationId": self.application,
            "token": self.token
        }

        utc = datetime.timezone.utc

        url = self.url + "resource/" + resource + "/meterread"

        resp = self.session.get(url, headers=headers)

        if resp.status_code != 200:
            raise RuntimeError("Request failed")

        resp = resp.json()

        if len(resp["data"]) < 1:
            raise RuntimeError("Meter reading not returned")

        if resp["units"] == "pence":
            cls = Pence
        elif resp["units"] == "kWh":
            cls = KWH
        else:
            cls = Unknown

        return [
            [datetime.datetime.fromtimestamp(v[0], tz = utc), cls(v[1])]
            for v in resp["data"]
        ]

    def get_tariff(self, resource):

        headers = {
            "Content-Type": "application/json",
            "applicationId": self.application,
            "token": self.token
        }

        url = self.url + "resource/" + resource + "/tariff"

        resp = self.session.get(url, headers=headers)

        if resp.status_code != 200:
            raise RuntimeError("Request failed")

        resp = resp.json()

        ts = []

        for elt in resp["data"]:

            t = Tariff()
            t.name = elt["name"]
            t.commodity = elt["commodity"]
            t.cid = elt["cid"]
            t.type = elt["type"]

            rt = Rate()
            rt.rate = Pence(elt["currentRates"]["rate"])
            rt.standing_charge = Pence(elt["currentRates"]["standingCharge"])
            rt.tier = None
            
            t.current_rates = rt

            # rts = []
            # for elt2 in elt["structure"]:

            #     rt = Rate()
            #     rt.rate = elt2["planDetail"]["rate"]
            #     rt.standing_charge = elt2["planDetail"]["standing"]
            #     rt.tier = elt2["planDetail"]["tier"]
            #     rts.append(rt)

            # t.structure = rts
        
        return t

