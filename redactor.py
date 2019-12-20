import sys
import time
from PyQt5 import QtGui, QtWidgets, QtCore
import model
from geometry import Matrix, Vector3
from objects import Point, Line, Polygon, Sphere, Cylinder
from drawer import Drawer
import math
from enum import Enum
from color import Color
from borderStyle import BorderStyle
from surfaceStyle import SurfaceStyle
import asyncio


RESOLUTION = (1280, 720)


class Mode(Enum):
    VIEW = 0
    EDIT = 1
    RESIZE = 2
    DELETE = 8
    CROSS = 9
    STYLE = 10
    POINT = 3
    LINE = 4
    POLYGON = 5
    SPHERE = 6
    CYLINDER = 7


class SceneWindow(QtWidgets.QLabel):
    def __init__(self, window):
        super().__init__(window)

        canvas = QtGui.QPixmap(RESOLUTION[0], RESOLUTION[1])
        canvas.fill(QtGui.QColor('grey'))
        self.setPixmap(canvas)

        self.last_x = 0
        self.last_y = 0
        self.zoom = 1
        self.last_time_clicked = time.time()
        self.forget_object_delay = 0.15
        self.object_to_interact = None

        self.split_coordinates = [640, 360]

        self.drawer = None
        self.style_preset = 81

        self.startTimer(20)

    def timerEvent(self, event):
        self.update_statusbar()

    def update_scene_display(self):
        with self.get_painter() as painter:
            self.drawer.update_scene(
                painter, RESOLUTION, self.split_coordinates, self.zoom)

        self.update_statusbar()

    def get_painter(self):
        return QtGui.QPainter(self.pixmap())

    def wheelEvent(self, event):
        if self.zoom < 0.15:
            self.zoom = max(self.zoom, self.zoom+event.angleDelta().y()/2880)
        elif self.zoom > 10:
            self.zoom = min(self.zoom, self.zoom+event.angleDelta().y()/2880)
        else:
            self.zoom += event.angleDelta().y()/2880
        self.parent().update_display()

    def mousePressEvent(self, event):
        if self.parent().mode == Mode.POINT:
            self.set_point(event)
        elif self.parent().mode == Mode.LINE:
            self.choose_line_points(event)
        elif self.parent().mode == Mode.POLYGON:
            self.choose_polygon_points(event)
        elif self.parent().mode == Mode.SPHERE:
            self.set_sphere(event)
        elif self.parent().mode == Mode.DELETE:
            self.delete_object(event)
        elif self.parent().mode == Mode.CROSS:
            self.choose_cross_object(event)
        elif self.parent().mode == Mode.STYLE:
            self.set_current_style_to_object(event)

        self.object_to_interact = None
        self.refresh_interaction_variables(event)
        self.parent().update_display()

    def calc_x(self, x):
        return x / self.zoom

    def calc_y(self, y):
        return y / self.zoom

    def refresh_interaction_variables(self, event):
        self.last_x = self.calc_x(event.x())
        self.last_y = self.calc_y(event.y())
        self.last_time_clicked = time.time()

    def set_point(self, event):
        self.parent().model.add_point((self.parent(
        ).model.display_plate_basis[0] *
            (self.calc_x(event.x() -
                         self.split_coordinates[0]))) +
            (self.parent(
            ).model.display_plate_basis[1] *
            (self.calc_y(event.y() -
                         self.split_coordinates[1]))),
            self.drawer.point_color)

    def set_sphere(self, event):
        self.parent().model.add_sphere((self.parent(
        ).model.display_plate_basis[0] *
            (self.calc_x(event.x() -
                         self.split_coordinates[0]))) +
            (self.parent(
            ).model.display_plate_basis[1] *
            (self.calc_y(event.y() -
                         self.split_coordinates[1]))),
            self.drawer.sphere_border_color,
            self.drawer.sphere_border_style,
            self.drawer.sphere_color,
            self.drawer.sphere_style)

    def choose_line_points(self, event):
        self.update_object_to_interact(event)
        if self.object_to_interact and isinstance(self.object_to_interact,
                                                  Point):
            self.parent().buffer.append(self.object_to_interact)
        if len(self.parent().buffer) == 2:
            self.parent().model.add_line(self.parent().buffer[0],
                                         self.parent().buffer[1],
                                         self.drawer.line_color,
                                         self.drawer.line_style)
            self.parent().buffer = []

    def choose_polygon_points(self, event):
        self.update_object_to_interact(event)
        if self.object_to_interact and isinstance(self.object_to_interact,
                                                  Point):
            self.parent().buffer.append(self.object_to_interact)

    def delete_object(self, event):
        self.update_object_to_interact(event)
        if self.object_to_interact:
            self.parent().model.objects.remove(self.object_to_interact)

    def choose_cross_object(self, event):
        self.update_object_to_interact(event)
        if self.object_to_interact:
            self.parent().buffer.append(self.object_to_interact)
        if len(self.parent().buffer) == 2:
            cross = self.parent().model.get_cross(self.parent().buffer[0],
                                                  self.parent().buffer[1])

            points = []
            for vector in cross:
                point = self.parent().model.search_or_add(
                    Point(vector.x, vector.y, vector.z,
                          self.drawer.point_color))
                points.append(point)
            if len(cross) >= 2:
                self.parent().model.add_line(points[0], points[1],
                                             self.drawer.line_color,
                                             self.drawer.line_style)
            self.parent().mode = Mode.VIEW
            self.parent().buffer = []

    def set_current_style_to_object(self, event):
        self.update_object_to_interact(event)
        if self.object_to_interact:
            self.object_to_interact.set_style(self.drawer)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self.parent().mode == Mode.VIEW:
            self.split_coordinates[0] += self.calc_x(event.x()) - self.last_x
            self.split_coordinates[1] += self.calc_y(event.y()) - self.last_y
        elif self.parent().mode == Mode.EDIT:
            self.edit_object(event)
        elif self.parent().mode == Mode.RESIZE:
            self.resize_object(event)

        self.refresh_interaction_variables(event)
        self.parent().update_display()

    def update_statusbar(self):
        pos = QtGui.QCursor.pos()
        global_coord = (self.parent().model.display_plate_basis[0] *
                        (self.calc_x(pos.x()) - self.split_coordinates[0]) +
                        self.parent().model.display_plate_basis[1] *
                        (self.calc_y(pos.y()) - self.split_coordinates[1]))
        self.parent().statusBar().showMessage(
            f'Mode: {str(self.parent().mode)[5:]}; x={round(global_coord.x, 1)} ' +
            f'y={round(global_coord.y, 1)} z={round(global_coord.z, 1)}; Zoom: {round(self.zoom, 2)}')

    def edit_object(self, event):
        if (self.object_to_interact and time.time() - self.last_time_clicked <
                self.forget_object_delay):  # maybe need more
            self.object_to_interact + (
                self.parent().model.display_plate_basis[0] *
                (self.calc_x(event.x()) - self.last_x) +
                self.parent().model.display_plate_basis[1] *
                (self.calc_y(event.y()) - self.last_y))
        else:
            self.update_object_to_interact(event)

    def resize_object(self, event):
        if (self.object_to_interact and time.time() - self.last_time_clicked <
                self.forget_object_delay):  # maybe need more
            if self.object_to_interact.RESIZABLE:  # to sphere
                self.object_to_interact.resize(
                    -self.get_distance(
                        self.last_x, self.last_y,
                        self.drawer.points_display_table[
                            self.object_to_interact.point][0],
                        self.drawer.points_display_table[
                            self.object_to_interact.point][1]) +
                    self.get_distance_to_point(event,
                                               self.object_to_interact.point))
        else:
            self.update_object_to_interact(event)

    # can we interact with poly or line ?... hmmm
    def update_object_to_interact(self, event):
        self.object_to_interact = None
        for obj in self.drawer.displayed_objects:
            if isinstance(obj, Point):
                distance = self.get_distance_to_point(event, obj)
                if obj.WIDTH > distance:
                    self.object_to_interact = obj
                    break
            elif isinstance(obj, Line):
                distance = self.get_distance_to_line(event, obj)
                if obj.WIDTH > distance:
                    self.object_to_interact = obj
                    break
            elif isinstance(obj, Polygon):
                is_inside = self.is_inside_polygon(event, obj)
                if is_inside:
                    self.object_to_interact = obj
                    break
            elif isinstance(obj, Sphere):
                distance = self.get_distance_to_sphere(event, obj)
                if obj.radius > distance:
                    self.object_to_interact = obj
                    break

    def get_distance(self, x0, y0, x1, y1):
        return math.sqrt((x0 - x1)**2 + (y0 - y1)**2)

    def get_distance_to_point(self, event, point):
        return self.get_distance(event.x(), event.y(),
                                 *self.drawer.points_display_table[point])

    def get_distance_to_sphere(self, event, sphere):
        return self.get_distance(
            event.x(), event.y(),
            *self.drawer.points_display_table[sphere.point])

    def get_distance_to_line(self, event, line):
        return (self.get_distance_to_point(event, line.start) +
                self.get_distance_to_point(event, line.end) -
                self.get_distance(
                    *self.drawer.points_display_table[line.start],
                    *self.drawer.points_display_table[line.end]))

    def is_inside_polygon(self, event, polygon):  # raycast alg
        x = event.x()
        y = event.y()

        is_inside = False
        last_point = polygon.points[len(polygon.points) - 1]
        for point in polygon.points:
            xi = self.drawer.points_display_table[point][0]
            yi = self.drawer.points_display_table[point][1]
            xj = self.drawer.points_display_table[last_point][0]
            yj = self.drawer.points_display_table[last_point][1]

            intersect = ((yi > y) != (yj > y)) and (
                x < (xj - xi) * (y - yi) / (yj - yi) + xi)
            if intersect:
                is_inside = not is_inside
            last_point = point

        return is_inside


class RedactorWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.model = None

        self.buffer = []

        self.drawer = None

        self.modes = {
            QtCore.Qt.Key_Q: Mode.EDIT,
            QtCore.Qt.Key_E: Mode.VIEW,
            QtCore.Qt.Key_R: Mode.RESIZE,
            QtCore.Qt.Key_L: Mode.LINE,
            QtCore.Qt.Key_P: Mode.POLYGON,
            QtCore.Qt.Key_T: Mode.CROSS}

        self.display_axiss = True

        rotate_angle = math.pi / 90
        self.rotate = {
            QtCore.Qt.Key_W: Matrix(3, 3, math.cos(rotate_angle),
                                    -math.sin(rotate_angle), 0,
                                    math.sin(rotate_angle),
                                    math.cos(rotate_angle),
                                    0, 0, 0, 1),
            QtCore.Qt.Key_R: Matrix(3, 3, 1, 0, 0, 0,
                                    math.cos(rotate_angle),
                                    -math.sin(rotate_angle), 0,
                                    math.sin(rotate_angle),
                                    math.cos(rotate_angle)),
            QtCore.Qt.Key_S: Matrix(3, 3, math.cos(-rotate_angle),
                                    -math.sin(-rotate_angle), 0,
                                    math.sin(-rotate_angle),
                                    math.cos(-rotate_angle),
                                    0, 0, 0, 1),
            QtCore.Qt.Key_A: Matrix(3, 3, math.cos(rotate_angle), 0,
                                    math.sin(rotate_angle), 0, 1, 0,
                                    -math.sin(rotate_angle), 0,
                                    math.cos(rotate_angle)),

            QtCore.Qt.Key_D: Matrix(3, 3, math.cos(-rotate_angle), 0,
                                    math.sin(-rotate_angle), 0, 1, 0,
                                    -math.sin(-rotate_angle), 0,
                                    math.cos(-rotate_angle))
        }

        self.mode = Mode.VIEW

        self.init_GUI()

        self.init_new_model()

    def init_GUI(self):
        self.setGeometry(0, 0, RESOLUTION[0], RESOLUTION[1])  # x y wide tall
        icon = QtGui.QIcon('textures/icon.png')
        self.setWindowIcon(icon)
        self.setWindowTitle('Black Box editor')

        new_scene_action = self.new_action(
            'New', self.init_new_model, 'textures/new.png')
        save_action = self.new_action(
            'Save', self.save_model, 'textures/save.png', 'Ctrl+S')
        open_action = self.new_action(
            'Open', self.open_model, 'textures/open.png')
        screen_action = self.new_action(
            'Scr', self.screenshot, 'textures/screen.png')
        point_action = self.new_action(
            'Point', lambda _: self.set_mode(Mode.POINT),
            'textures/pt.png', '1')
        line_action = self.new_action(
            'Line', lambda _: self.set_mode(Mode.LINE),
            'textures/ln.png', '2')
        polygon_action = self.new_action(
            'Polygon', lambda _: self.set_mode(Mode.POLYGON),
            'textures/plg.png', '3')
        sphere_action = self.new_action(
            'Sphere', lambda _: self.set_mode(Mode.SPHERE),
            'textures/sp.png', '4')
        delete_action = self.new_action(
            'Delete', lambda _: self.set_mode(Mode.DELETE),
            'textures/delete.png')
        point_color_action_red = self.new_action(
            'Red', lambda _: setattr(self.label.drawer,
                                     'point_color', Color.RED))
        point_color_action_orange = self.new_action(
            'Orange', lambda _: setattr(self.label.drawer,
                                        'point_color', Color.ORANGE_LIGHT))
        point_color_action_yellow = self.new_action(
            'Yellow', lambda _: setattr(self.label.drawer,
                                        'point_color', Color.YELLOW))
        line_style_action_solid = self.new_action(
            'Solid', lambda _: setattr(self.label.drawer,
                                       'line_style', BorderStyle.SOLID))
        line_style_action_dash = self.new_action(
            'Dash', lambda _: setattr(self.label.drawer,
                                      'line_style', BorderStyle.DASH))
        line_style_action_dashdot = self.new_action(
            'Dash Dot', lambda _: setattr(self.label.drawer,
                                          'line_style', BorderStyle.DASH_DOT))
        line_style_action_dashdotdot = self.new_action(
            'Dash Dot Dot', lambda _: setattr(self.label.drawer,
                                              'line_style',
                                              BorderStyle.DASH_DOT_DOT))
        line_color_action_red = self.new_action(
            'Red', lambda _: setattr(self.label.drawer,
                                     'line_color', Color.RED))
        line_color_action_orange = self.new_action(
            'Orange', lambda _: setattr(self.label.drawer,
                                        'line_color', Color.ORANGE_LIGHT))
        line_color_action_yellow = self.new_action(
            'Yellow', lambda _: setattr(self.label.drawer,
                                        'line_color', Color.YELLOW))
        polygon_border_style_action_solid = self.new_action(
            'Solid', lambda _: setattr(self.label.drawer,
                                       'polygon_border_style', BorderStyle.SOLID))
        polygon_border_style_action_dash = self.new_action(
            'Dash', lambda _: setattr(self.label.drawer,
                                      'polygon_border_style', BorderStyle.DASH))
        polygon_border_style_action_dashdot = self.new_action(
            'Dash Dot', lambda _: setattr(self.label.drawer,
                                          'polygon_border_style', BorderStyle.DASH_DOT))
        polygon_border_style_action_dashdotdot = self.new_action(
            'Dash Dot Dot', lambda _: setattr(self.label.drawer,
                                              'polygon_border_style',
                                              BorderStyle.DASH_DOT_DOT))
        polygon_border_color_action_red = self.new_action(
            'Red', lambda _: setattr(self.label.drawer,
                                     'polygon_border_color', Color.RED))
        polygon_border_color_action_orange = self.new_action(
            'Orange', lambda _: setattr(self.label.drawer,
                                        'polygon_border_color', Color.ORANGE_LIGHT))
        polygon_border_color_action_yellow = self.new_action(
            'Yellow', lambda _: setattr(self.label.drawer,
                                        'polygon_border_color', Color.YELLOW))
        polygon_style_action_solid = self.new_action(
            'Solid', lambda _: setattr(self.label.drawer,
                                       'polygon_style', SurfaceStyle.SOLID))
        polygon_style_action_dense = self.new_action(
            'Dense', lambda _: setattr(self.label.drawer,
                                       'polygon_style', SurfaceStyle.DENSE))
        polygon_style_action_diagcross = self.new_action(
            'Diag cross', lambda _: setattr(self.label.drawer,
                                            'polygon_style', SurfaceStyle.DIAGCROSS))
        polygon_color_action_red = self.new_action(
            'Red', lambda _: setattr(self.label.drawer,
                                     'polygon_color', Color.RED))
        polygon_color_action_orange = self.new_action(
            'Orange', lambda _: setattr(self.label.drawer,
                                        'polygon_color', Color.ORANGE_DARK))
        polygon_color_action_yellow = self.new_action(
            'Yellow', lambda _: setattr(self.label.drawer,
                                        'polygon_color', Color.YELLOW))

        sphere_border_style_action_solid = self.new_action(
            'Solid', lambda _: setattr(self.label.drawer,
                                       'sphere_border_style', BorderStyle.SOLID))
        sphere_border_style_action_dash = self.new_action(
            'Dash', lambda _: setattr(self.label.drawer,
                                      'sphere_border_style', BorderStyle.DASH))
        sphere_border_style_action_dashdot = self.new_action(
            'Dash Dot', lambda _: setattr(self.label.drawer,
                                          'sphere_border_style', BorderStyle.DASH_DOT))
        sphere_border_style_action_dashdotdot = self.new_action(
            'Dash Dot Dot', lambda _: setattr(self.label.drawer,
                                              'sphere_border_style',
                                              BorderStyle.DASH_DOT_DOT))
        sphere_border_color_action_red = self.new_action(
            'Red', lambda _: setattr(self.label.drawer,
                                     'sphere_border_color', Color.RED))
        sphere_border_color_action_orange = self.new_action(
            'Orange', lambda _: setattr(self.label.drawer,
                                        'sphere_border_color', Color.ORANGE_LIGHT))
        sphere_border_color_action_yellow = self.new_action(
            'Yellow', lambda _: setattr(self.label.drawer,
                                        'sphere_border_color', Color.YELLOW))
        sphere_style_action_solid = self.new_action(
            'Solid', lambda _: setattr(self.label.drawer,
                                       'sphere_style', SurfaceStyle.SOLID))
        sphere_style_action_dense = self.new_action(
            'Dense', lambda _: setattr(self.label.drawer,
                                       'sphere_style', SurfaceStyle.DENSE))
        sphere_style_action_diagcross = self.new_action(
            'Diag cross', lambda _: setattr(self.label.drawer,
                                            'sphere_style', SurfaceStyle.DIAGCROSS))
        sphere_color_action_red = self.new_action(
            'Red', lambda _: setattr(self.label.drawer,
                                     'sphere_color', Color.RED))
        sphere_color_action_orange = self.new_action(
            'Orange', lambda _: setattr(self.label.drawer,
                                        'sphere_color', Color.ORANGE_DARK))
        sphere_color_action_yellow = self.new_action(
            'Yellow', lambda _: setattr(self.label.drawer,
                                        'sphere_color', Color.YELLOW))

        edit_mode = self.new_action(
            'Edit', lambda _: self.set_mode(Mode.EDIT), shortcut='Q')
        view_mode = self.new_action(
            'View', lambda _: self.set_mode(Mode.VIEW), shortcut='E')
        resize_mode = self.new_action(
            'Resize', lambda _: self.set_mode(Mode.RESIZE), shortcut='Ctrl+R')
        cross_mode = self.new_action(
            'Cross', lambda _: self.set_mode(Mode.CROSS), shortcut='Ctrl+T')
        style_mode = self.new_action(
            'Style', lambda _: self.set_mode(Mode.STYLE), shortcut='C')
        # TODO Modes menu
        menubar = self.menuBar()
        menubar.setStyleSheet("""QMenuBar {
         background-color: rgb(220,150,120);
        }

     QMenuBar::item {
         background: rgb(220,150,120);
     }""")
        fileMenu = menubar.addMenu('Files')  # menu
        fileMenu.addAction(new_scene_action)
        fileMenu.addAction(save_action)
        fileMenu.addAction(open_action)
        menubar.addAction(screen_action)
        settings = menubar.addMenu('Settings')
        pt_settings = settings.addMenu('Point')
        pt_settings.addAction(point_color_action_red)
        pt_settings.addAction(point_color_action_orange)
        pt_settings.addAction(point_color_action_yellow)
        ln_settings = settings.addMenu('Line')
        ln_settings_style = ln_settings.addMenu('Style')
        ln_settings_style.addAction(line_style_action_solid)
        ln_settings_style.addAction(line_style_action_dash)
        ln_settings_style.addAction(line_style_action_dashdot)
        ln_settings_style.addAction(line_style_action_dashdotdot)
        ln_settings_color = ln_settings.addMenu('Color')
        ln_settings_color.addAction(line_color_action_red)
        ln_settings_color.addAction(line_color_action_orange)
        ln_settings_color.addAction(line_color_action_yellow)
        pg_settings = settings.addMenu('Polygon')
        pg_settings_border_style = pg_settings.addMenu('Border Style')
        pg_settings_border_style.addAction(polygon_border_style_action_solid)
        pg_settings_border_style.addAction(polygon_border_style_action_dash)
        pg_settings_border_style.addAction(
            polygon_border_style_action_dashdot)
        pg_settings_border_style.addAction(
            polygon_border_style_action_dashdotdot)
        pg_settings_border_color = pg_settings.addMenu('Border Color')
        pg_settings_border_color.addAction(polygon_border_color_action_red)
        pg_settings_border_color.addAction(polygon_border_color_action_orange)
        pg_settings_border_color.addAction(polygon_border_color_action_yellow)
        pg_settings_style = pg_settings.addMenu('Style')
        pg_settings_style.addAction(polygon_style_action_solid)
        pg_settings_style.addAction(polygon_style_action_dense)
        pg_settings_style.addAction(polygon_style_action_diagcross)
        pg_settings_color = pg_settings.addMenu('Color')
        pg_settings_color.addAction(polygon_color_action_red)
        pg_settings_color.addAction(polygon_color_action_orange)
        pg_settings_color.addAction(polygon_color_action_yellow)
        sp_settings = settings.addMenu('Sphere')
        sp_settings_border_style = sp_settings.addMenu('Border Style')
        sp_settings_border_style.addAction(sphere_border_style_action_solid)
        sp_settings_border_style.addAction(sphere_border_style_action_dash)
        sp_settings_border_style.addAction(sphere_border_style_action_dashdot)
        sp_settings_border_style.addAction(
            sphere_border_style_action_dashdotdot)
        sp_settings_border_color = sp_settings.addMenu('Border Color')
        sp_settings_border_color.addAction(sphere_border_color_action_red)
        sp_settings_border_color.addAction(sphere_border_color_action_orange)
        sp_settings_border_color.addAction(sphere_border_color_action_yellow)
        sp_settings_style = sp_settings.addMenu('Style')
        sp_settings_style.addAction(sphere_style_action_solid)
        sp_settings_style.addAction(sphere_style_action_dense)
        sp_settings_style.addAction(sphere_style_action_diagcross)
        sp_settings_color = sp_settings.addMenu('Color')
        sp_settings_color.addAction(sphere_color_action_red)
        sp_settings_color.addAction(sphere_color_action_orange)
        sp_settings_color.addAction(sphere_color_action_yellow)
        mode_menu = menubar.addMenu('Modes')
        mode_menu.addAction(edit_mode)
        mode_menu.addAction(view_mode)
        mode_menu.addAction(resize_mode)
        mode_menu.addAction(cross_mode)
        mode_menu.addAction(style_mode)
        toolbar = QtWidgets.QToolBar(self)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, toolbar)
        toolbar.addAction(point_action)
        toolbar.addAction(line_action)
        toolbar.addAction(polygon_action)
        toolbar.addAction(sphere_action)
        toolbar.addAction(delete_action)
        self.statusBar()

        self.label = SceneWindow(self)
        self.setCentralWidget(self.label)

    def new_action(self, name, connect_with, icon=None, shortcut=None):
        action = QtWidgets.QAction(
            QtGui.QIcon(icon), name, self)
        action.triggered.connect(connect_with)
        if shortcut:
            action.setShortcut(shortcut)
        return action

    def update_display(self):
        self.label.update_scene_display()
        self.update()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if not self.model:
            return
        if event.key() == QtCore.Qt.Key_CapsLock:
            self.display_axiss = not self.display_axiss
        # elif event.key() in self.modes:  # if we change when polygon
        #   self.set_mode(self.modes[event.key()])
        elif event.key() in self.rotate:
            self.model.update_display_matrix(self.rotate[event.key()])
        self.update_display()

    def set_mode(self, mode: Mode):  # deconstructors for modes
        if self.mode == Mode.POLYGON and len(self.buffer) > 2:
            self.model.add_polygon(self.buffer,
                                   self.label.drawer.polygon_border_color,
                                   self.label.drawer.polygon_border_style,
                                   self.label.drawer.polygon_color,
                                   self.label.drawer.polygon_style)
        self.buffer = []
        self.mode = mode
        self.update_display()

    def init_new_model(self):
        del(self.model)
        self.model = model.Model()
        self.label.drawer = Drawer(self.model)
        self.update_display()

    def open_model(self):  # show the window where we can write filename
        filename, ok = QtWidgets.QInputDialog.getText(
            self, 'Filename',
            'Enter the filename for open:')
        if not ok:
            return
        self.model = model.Model()
        try:
            with open(filename, 'r', encoding='utf8') as file:
                self.model.open(file)
        except FileNotFoundError:
            QtWidgets.QMessageBox.about(self, 'Error', 'File not found')
        self.label.drawer = Drawer(self.model)
        self.update_display()

    def save_model(self):  # show the window where we can write filename
        if not self.model:
            return
        filename, ok = QtWidgets.QInputDialog.getText(
            self, 'Filename',
            'Enter the filename for save:')
        if not ok:
            return
        try:
            with open(filename, 'w', encoding='utf8') as file:
                self.model.save(file)
        except PermissionError:
            QtWidgets.QMessageBox.about(self, 'Error', 'Permission Error')
        self.update_display()

    def screenshot(self, filename):
        filename, ok = QtWidgets.QInputDialog.getText(
            self, 'Filename',
            'Enter the filename to save screen:')
        if not ok:
            return
        screen = QtWidgets.QApplication.primaryScreen()
        if not filename.endswith('.png'):
            filename += '.png'
        try:
            screen.grabWindow(self.winId()).save(filename, 'png')
        except PermissionError:
            QtWidgets.QMessageBox.about(self, 'Error', 'Permission Error')
