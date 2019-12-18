class Serializable:
    def __init__(self, fields):
        self.fields = fields

    def __dict__(self):# need to __NAME__ = True attr 
        res = {}
        for field in self.fields: 
            attr = getattr(self, field)
            if isinstance(attr, Serializable):
                res[field] = dict(attr)
            else:
                res[field] = attr
        return res

    def initialize(self, obj_dict: dict, objects):
        for field in obj_dict:
            setattr(self, field, obj_dict[field])  # if point it will be dict(point)
        self.extra_initialize(objects)

    def extra_initialize(self, objects):
        raise NotImplementedError()

