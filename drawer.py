from objects import Point, Line, Polygon, Sphere, Cylinder
from PyQt5 import QtGui, QtWidgets, QtCore


class Drawer:
    def __init__(self, model):
        self.model = model
        self.displayed_objects = []  # to hide objects later
        self.points_display_table = {}

        self.style = {
            'point color': QtGui.QColor(255, 102, 0),
            'line style': QtCore.Qt.SolidLine,
            'line width': 5,
            'line color': QtGui.QColor(255, 102, 0),
            'polygon border style': QtCore.Qt.SolidLine,
            'polygon border color': QtGui.QColor(255, 102, 0),
            'polygon style': QtCore.Qt.SolidPattern,
            'polygon color': QtGui.QColor(230, 102, 30),
            'sphere border style': QtCore.Qt.SolidLine,
            'sphere border color': QtGui.QColor(255, 102, 0),
            'sphere style': QtCore.Qt.SolidPattern,
            'sphere color': QtGui.QColor(230, 102, 30)
        }

        self.scene_style_preset = 81
        self.axiss_size = 50
        self.axiss_width = 3

        self.draw_table = {
            Point: self.paint_pt,
            Line: self.paint_ln,
            Polygon: self.paint_pg,
            Sphere: self.paint_sp,
            Cylinder: self.paint_cl
        }

        self.check_to_visible = {
            Point: lambda point: model.get_plate_equation_value(point.x,
                                                                point.y,
                                                                point.z) >= 0,
            Line: lambda line: any(model.get_plate_equation_value(line.start.x,
                                                                  line.start.y,
                                                                  line.start.z) >= 0,
                                   model.get_plate_equation_value(line.end.x,
                                                                  line.end.y,
                                                                  line.end.z) >= 0),
            Polygon: lambda polygon: any((model.get_plate_equation_value(point.x,
                                                                         point.y,
                                                                         point.z) >= 0 for point in polygon.points)),
            Sphere: lambda sphere: model.get_plate_equation_value(sphere.point.x,
                                                                  sphere.point.y,
                                                                  sphere.point.z) >= 0,
            Cylinder: self.paint_cl
        }

    def update_scene(self, painter, resolution, split_coordinates):
        painter.fillRect(
            0, 0, resolution[0], resolution[1], QtGui.QGradient.Preset(self.scene_style_preset))

        self.draw_coordinates_system(painter)

        for obj in self.model.objects:
            self.paint_object(
                obj, split_coordinates, painter)

    def paint_object(self, obj, split_coordinates, painter):
        for obj in self.model.objects:
            if isinstance(obj, Point):
                display_coord = self.model.display_vector(
                    obj.to_vector3())
                self.points_display_table[obj] = (display_coord[0] +
                                                  split_coordinates[0],
                                                  display_coord[1] +
                                                  split_coordinates[1])
            #if self.is_visible(obj): # for perspective need
            self.draw_table[type(obj)](obj, painter)
            self.displayed_objects.append(obj)

    def is_visible(self, obj):
        return self.check_to_visible[type(obj)](obj)

    def paint_pt(self, point, painter):
        painter.drawEllipse(self.points_display_table[point][0] -
                            point.WIDTH / 2,
                            self.points_display_table[point][1] -
                            point.WIDTH / 2,
                            point.WIDTH, point.WIDTH)

    def paint_ln(self, line, painter):
        painter.pen().setWidth(line.WIDTH)
        painter.drawLine(
            *self.points_display_table[line.start],
            *self.points_display_table[line.end])

    def paint_pg(self, polygon, painter):
        painter.pen().setWidth(polygon.WIDTH)
        painter.drawConvexPolygon(
            *[QtCore.QPointF(*self.points_display_table[point])
              for point in polygon.points])

    def paint_sp(self, sphere, painter):
        width = 2*sphere.radius
        painter.drawEllipse(self.points_display_table[sphere.point][0] -
                            width / 2,
                            self.points_display_table[sphere.point][1] -
                            width / 2,
                            width, width)

    def paint_cl(self, cylinder, painter):
        painter.pen().setWidth(2*cylinder.radius)
        painter.drawLine(
            *self.points_display_table[cylinder.line.start],
            *self.points_display_table[cylinder.line.end])
        # print 2 ellipse

    def draw_coordinates_system(self, painter):
        painter.setPen(QtGui.QPen(QtCore.Qt.white, self.axiss_width,
                                  QtCore.Qt.SolidLine))
        width = 5
        display_origin = self.model.display_vector(
            self.model.origin.to_vector3())
        display_origin = (display_origin[0] + 1200,
                          display_origin[1] + 60)
        painter.drawEllipse(display_origin[0] - width / 2,
                            display_origin[1] - width / 2,
                            width, width)

        painter.setPen(QtGui.QPen(QtCore.Qt.green, self.axiss_width,
                                  QtCore.Qt.DashLine))
        self.draw_axis(painter, self.model.basis[0], display_origin)

        painter.setPen(QtGui.QPen(QtCore.Qt.blue, self.axiss_width,
                                  QtCore.Qt.DashLine))
        self.draw_axis(painter, self.model.basis[1], display_origin)

        painter.setPen(QtGui.QPen(QtCore.Qt.red, self.axiss_width,
                                  QtCore.Qt.DashLine))
        self.draw_axis(painter, self.model.basis[2], display_origin)

        painter.setPen(QtGui.QPen(QtGui.QColor(
            255, 102, 0), 5, QtCore.Qt.SolidLine))

    def draw_axis(self, painter, basis_vector, display_origin):
        width = 5
        temp_point = Point(basis_vector.x * self.axiss_size,
                           basis_vector.y * self.axiss_size,
                           basis_vector.z * self.axiss_size)
        display_coord = self.model.display_vector(
            temp_point.to_vector3())
        display_coord = (display_coord[0] + 1200,
                         display_coord[1] + 60)
        painter.drawEllipse(display_coord[0] - width / 2,
                            display_coord[1] - width / 2,
                            width, width)
        painter.drawLine(  # from start to end
            *display_origin,
            *display_coord)
