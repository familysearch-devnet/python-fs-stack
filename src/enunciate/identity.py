try:
    import json
except ImportError:
    import simplejson as json


def parse(input):
    """Parse specified file or string and return an Identity object created from it."""
    if hasattr(input, "read"):
        data = json.load(input)
    else:
        data = json.loads(input)
    return Identity(data)


class JSONBase:
    """Base class for all JSON-related objects"""
    def to_json(self):
        return json.dumps(self.to_json_dict())

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.to_json_dict())

    def __str__(self):
        return self.to_json()


class FSDict(dict):
    """Convenience class to access FamilySearch-style property lists as dictionaries
    
    For example,
        [{"name": "key1", "value": "value1"}, {"name": "key2", "value": "value2"}]
    converts to
        {"key1": "value1", "key2": "value2"}
    
    """

    def __init__(self, pairs=None):
        if isinstance(pairs, list) and all((isinstance(pair, dict) for pair in pairs)):
            dict.__init__(self)
            for pair in pairs:
                self[pair["name"]] = pair["value"]

    def to_json_array(self):
        return [{"name": key, "value": self[key]} for key in self]


class Identity(JSONBase):
    def __init__(self, o):
        if "statusCode" in o:
            self.statusCode = o["statusCode"]
        if "statusMessage" in o:
            self.statusMessage = o["statusMessage"]
        if "version" in o:
            self.version = o["version"]
        if "properties" in o:
            self.properties = FSDict(o["properties"])
        if "session" in o:
            self.session = Session(o["session"])

    def to_json_dict(self):
        d = {}
        if hasattr(self, "statusCode"):
            d["statusCode"] = self.statusCode
        if hasattr(self, "statusMessage"):
            d["statusMessage"] = self.statusMessage
        if hasattr(self, "version"):
            d["version"] = self.version
        if hasattr(self, "properties"):
            d["properties"] = self.properties.to_json_array()
        if hasattr(self, "session"):
            d["session"] = self.session.to_json_dict()
        return d


class Session(JSONBase):
    def __init__(self, o):
        if "id" in o:
            self.id = o["id"]
        if "type" in o:
            self.type = o["type"]

    def to_json_dict(self):
        d = {}
        if hasattr(self, "id"):
            d["id"] = self.id
        if hasattr(self, "type"):
            d["type"] = self.type
        return d
