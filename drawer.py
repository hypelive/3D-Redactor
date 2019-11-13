from objects import Point, Line, Polygon, Sphere, Cylinder
from PyQt5 import QtGui, QtWidgets, QtCore


class Drawer:
    def __init__(self, model):
        self.model = model
        self.points_display_table = {}
        self.draw_table = {
            Point: self.paint_pt,
            Line: self.paint_ln,
            Polygon: self.paint_pg,
            Sphere: self.paint_sp,
            Cylinder: self.paint_cl
        }

    def paint_object(self, obj, split_coordinates, painter):
        for obj in self.model.objects:
            if isinstance(obj, Point):
                display_coord = self.model.display_vector(
                    obj.to_vector3())
                self.points_display_table[obj] = (display_coord[0] +
                                                  split_coordinates[0],
                                                  display_coord[1] +
                                                  split_coordinates[1])
            self.draw_table[type(obj)](obj, painter)

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

    def draw_coordinates_system(self, split_coordinates, axiss_width,
                                axiss_size, painter):
        painter.setPen(QtGui.QPen(QtCore.Qt.black, axiss_width,
                                  QtCore.Qt.SolidLine))
        width = 5
        display_origin = self.model.display_vector(
            self.model.origin.to_vector3())
        display_origin = (display_origin[0] + split_coordinates[0],
                          display_origin[1] + split_coordinates[1])
        painter.drawEllipse(display_origin[0] - width / 2,
                            display_origin[1] - width / 2,
                            width, width)

        painter.setPen(QtGui.QPen(QtCore.Qt.green, axiss_width,
                                  QtCore.Qt.SolidLine))
        self.draw_axis(painter, self.model.basis[0], display_origin,
                       split_coordinates, axiss_size)

        painter.setPen(QtGui.QPen(QtCore.Qt.blue, axiss_width,
                                  QtCore.Qt.SolidLine))
        self.draw_axis(painter, self.model.basis[1], display_origin,
                       split_coordinates, axiss_size)

        painter.setPen(QtGui.QPen(QtCore.Qt.red, axiss_width,
                                  QtCore.Qt.SolidLine))
        self.draw_axis(painter, self.model.basis[2], display_origin,
                       split_coordinates, axiss_size)

        painter.setPen(QtGui.QPen(QtGui.QColor(
            255, 102, 0), 5, QtCore.Qt.SolidLine))

    def draw_axis(self, painter, basis_vector, display_origin,
                  split_coordinates, axiss_size):
        width = 5
        temp_point = Point(basis_vector.x * axiss_size,
                           basis_vector.y * axiss_size,
                           basis_vector.z * axiss_size)
        display_coord = self.model.display_vector(
            temp_point.to_vector3())
        display_coord = (display_coord[0] + split_coordinates[0],
                         display_coord[1] + split_coordinates[1])
        painter.drawEllipse(display_coord[0] - width / 2,
                            display_coord[1] - width / 2,
                            width, width)
        painter.drawLine(  # from start to end
            *display_origin,
            *display_coord)
