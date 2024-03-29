from enum import Enum


class Serializable:
    def __init__(self, fields):
        self.fields = fields

    def __dict__(self):  # need to __NAME__ = True attr
        res = {}
        res['NAME'] = getattr(self, 'NAME')
        for field in self.fields:
            attr = getattr(self, field)
            if isinstance(attr, Serializable):
                res[field] = attr.__dict__()
            elif isinstance(attr, list):
                res[field] = [entry.__dict__() for entry in attr]
            elif isinstance(attr, Enum):
                res[field] = attr.value
            else:
                res[field] = attr
        return res

    def initialize(self, obj_dict: dict, objects=None):
        for field in obj_dict:
            # if point it will be dict(point)
            setattr(self, field, obj_dict[field])
        self.extra_initialize(objects)
        return self

    def extra_initialize(self, objects):
        pass
