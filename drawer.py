from objects import Point, Line, Polygon, Sphere, Cylinder
from PyQt5 import QtGui, QtWidgets, QtCore
from color import Color
from borderStyle import BorderStyle
from surfaceStyle import SurfaceStyle

COLORS = {
    Color.RED: QtCore.Qt.red,
    Color.ORANGE_LIGHT: QtGui.QColor(255, 102, 0),
    Color.ORANGE_DARK: QtGui.QColor(230, 102, 30),
    Color.YELLOW: QtCore.Qt.yellow
}

BORDER_STYLES = {
    BorderStyle.SOLID: QtCore.Qt.SolidLine,
    BorderStyle.DASH: QtCore.Qt.DashLine,
    BorderStyle.DASH_DOT: QtCore.Qt.DashDotLine,
    BorderStyle.DASH_DOT_DOT: QtCore.Qt.DashDotDotLine
}

SURFACE_STYLES = {
    SurfaceStyle.SOLID: QtCore.Qt.SolidPattern,
    SurfaceStyle.DENSE: QtCore.Qt.Dense1Pattern,
    SurfaceStyle.DIAGCROSS: QtCore.Qt.DiagCrossPattern
}

class Drawer:
    def __init__(self, model):
        self.model = model
        self.displayed_objects = []  # to hide objects later
        self.points_display_table = {}

        self.style_settings = {}

        self.point_color = Color.ORANGE_LIGHT
        self.line_color = Color.ORANGE_LIGHT
        self.line_style = BorderStyle.SOLID
        self.polygon_border_color = Color.ORANGE_LIGHT
        self.polygon_border_style = BorderStyle.SOLID
        self.polygon_color = Color.ORANGE_DARK
        self.polygon_style = SurfaceStyle.SOLID
        self.sphere_border_color = Color.ORANGE_LIGHT
        self.sphere_border_style = BorderStyle.SOLID
        self.sphere_color = Color.ORANGE_DARK
        self.sphere_style = SurfaceStyle.SOLID

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
            Point: lambda point: model.get_plate_equation_value(
                point.x,
                point.y,
                point.z) >= 0,
            Line: lambda line: any(model.get_plate_equation_value(
                line.start.x,
                line.start.y,
                line.start.z) >= 0,
                model.get_plate_equation_value(
                line.end.x,
                line.end.y,
                line.end.z) >= 0),
            Polygon: lambda polygon: any((model.get_plate_equation_value(
                point.x,
                point.y,
                point.z) >= 0 for point in polygon.points)),
            Sphere: lambda sphere: model.get_plate_equation_value(
                sphere.point.x,
                sphere.point.y,
                sphere.point.z) >= 0,
            Cylinder: self.paint_cl
        }

    def set_style(self, stylename, param):
        #self.style[stylename] = param
        pass

    def update_scene(self, painter, resolution, split_coordinates, zoom):
        self.set_painter_params(painter)
        painter.fillRect(
            0, 0, resolution[0], resolution[1],
            QtGui.QGradient.Preset(self.scene_style_preset))

        self.draw_coordinates_system(painter)

        self.displayed_objects = []
        for obj in self.model.objects:
            self.paint_object(
                obj, split_coordinates, zoom, painter)

    def paint_object(self, obj, split_coordinates, zoom, painter):
        for obj in self.model.objects:
            if isinstance(obj, Point):
                display_coord = self.model.display_vector(
                    obj.to_vector3())
                self.points_display_table[obj] = (display_coord[0] * zoom +
                                                  split_coordinates[0],
                                                  display_coord[1] * zoom +
                                                  split_coordinates[1])
            # if not obj in self.style_settings:
            #    self.update_style(obj)
            # if self.is_visible(obj): # for perspective need
            self.draw_table[type(obj)](obj, painter, zoom)
            self.displayed_objects.append(obj)

    def is_visible(self, obj):
        return self.check_to_visible[type(obj)](obj)

    def set_painter_params(self, painter, pen_color=QtGui.QColor(230, 102, 0),
                           pen_width=5, pen_style=QtCore.Qt.SolidLine,
                           brush_color=QtGui.QColor(230, 102, 30),
                           brush_style=QtCore.Qt.SolidPattern):
        painter.setPen(QtGui.QPen(pen_color, pen_width, pen_style))
        painter.setBrush(QtGui.QBrush(brush_color, brush_style))

    def paint_pt(self, point, painter, zoom):
        self.set_painter_params(painter, pen_color=COLORS[point.color],
                                brush_color=COLORS[point.color])
        painter.drawEllipse(self.points_display_table[point][0] -
                            point.WIDTH / 2,
                            self.points_display_table[point][1] -
                            point.WIDTH / 2,
                            point.WIDTH, point.WIDTH)

    def paint_ln(self, line, painter, zoom):
        self.set_painter_params(painter, pen_style=BORDER_STYLES[line.style],
                                pen_color=COLORS[line.color])
        painter.pen().setWidth(line.WIDTH)
        painter.drawLine(
            *self.points_display_table[line.start],
            *self.points_display_table[line.end])

    def paint_pg(self, polygon, painter, zoom):
        self.set_painter_params(painter,
                                pen_style=BORDER_STYLES[polygon.border_style],
                                pen_color=COLORS[polygon.border_color],
                                brush_style=SURFACE_STYLES[polygon.style],
                                brush_color=COLORS[polygon.color])
        painter.pen().setWidth(polygon.WIDTH)
        painter.drawConvexPolygon(
            *[QtCore.QPointF(*self.points_display_table[point])
              for point in polygon.points])

    def paint_sp(self, sphere, painter, zoom):
        self.set_painter_params(painter,
                                pen_style=BORDER_STYLES[sphere.border_style],
                                pen_color=COLORS[sphere.border_color],
                                brush_color=COLORS[sphere.color],
                                brush_style=SURFACE_STYLES[sphere.style])
        width = 2*sphere.radius*zoom
        painter.drawEllipse(self.points_display_table[sphere.point][0] -
                            width / 2,
                            self.points_display_table[sphere.point][1] -
                            width / 2,
                            width, width)

    def paint_cl(self, cylinder, painter, zoom):
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
