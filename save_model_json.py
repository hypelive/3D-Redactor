def save_j(self, filename: str):
    with open(filename, 'w', encoding='utf8') as file:
        file.write(json.dumps(self.__dict__()))

def open_j(self, filename: str):
    dedictors = {
        '__Line__': Line.__dedict__,
        '__Polygon': Polygon.__dedict__
    }
    with open(filename, 'r', encoding='utf8') as file:
        model_dict = json.loads(file.read())
    if not '__Model__' in model_dict:
        raise Exception('unknown save file')
    self.basis = [Vector3(vector['x'], vector['y'], vector['z'])
                    for vector in model_dict['basis'] if '__Vector3__' in vector]
    self.origin = Point(
        model_dict['origin']['x'], model_dict['origin']['y'], model_dict['origin']['z'])
    self.display_plate_basis = [Vector3(vector['x'], vector['y'], vector['z'])
                                for vector in model_dict['display_plate_basis'] if '__Vector3__' in vector]
    for obj in model_dict['objects']:
        if '__Point__' in obj:
            self.objects.append(Point.__dedict__(obj))
    for obj in model_dict['objects']:
        for key in dedictors:
            if key in obj:
                self.objects.append(dedictors[key](obj, self.objects))


def __dict__(self):
    return {
        '__Model__': True,
        'basis': [vector.__dict__() for vector in self.basis],
        'origin': self.origin.__dict__(),
        'display_plate_basis': [vector.__dict__() for vector in self.display_plate_basis],
        'objects': [obj.__dict__() for obj in self.objects]
    }