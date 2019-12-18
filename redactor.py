import sys
import time
from PyQt5 import QtGui, QtWidgets, QtCore
import model
from geometry import Matrix, Vector3
from objects import Point, Line, Polygon, Sphere, Cylinder
from drawer import Drawer
import math
from enum import Enum

RESOLUTION = (1280, 720)


class Mode(Enum):
    VIEW = 0
    EDIT = 1
    RESIZE = 2
    DELETE = 8
    CROSS = 9
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

    def update_scene_display(self):
        with self.get_painter() as painter:
            self.drawer.update_scene(
                painter, RESOLUTION, self.split_coordinates, self.zoom)

            global_coord = (self.parent().model.display_plate_basis[0] *
                            self.last_x +
                            self.parent().model.display_plate_basis[1] *
                            self.last_y)
            self.parent().statusBar().showMessage(
                f'Mode: {str(self.parent().mode)[5:]}; x={global_coord.x} ' +
                f'y={global_coord.y} z={global_coord.z}; Zoom: {self.zoom}')

    def get_painter(self):
        return QtGui.QPainter(self.pixmap())

    def wheelEvent(self, event):
        if self.zoom < 0.15:
            self.zoom = max(self.zoom, self.zoom+event.angleDelta().y()/2880)
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
                         self.split_coordinates[1]))))

    def set_sphere(self, event):
        self.parent().model.add_sphere((self.parent(
        ).model.display_plate_basis[0] *
            (self.calc_x(event.x() -
                         self.split_coordinates[0]))) +
            (self.parent(
            ).model.display_plate_basis[1] *
            (self.calc_y(event.y() -
                         self.split_coordinates[1]))))

    def choose_line_points(self, event):
        self.update_object_to_interact(event)
        if self.object_to_interact and isinstance(self.object_to_interact,
                                                  Point):
            self.parent().buffer.append(self.object_to_interact)
        if len(self.parent().buffer) == 2:
            self.parent().model.add_line(self.parent().buffer[0],
                                         self.parent().buffer[1])
            self.parent().mode = Mode.VIEW
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
            if not cross:
                pass
            else:
                for vector in cross:
                    point = Point(vector.x, vector.y, vector.z)
                    points.append(point)
                    self.parent().model.add_point(point)
            if len(cross) >= 2:
                self.parent().model.add_line(points[0], points[1])
            self.parent().mode = Mode.VIEW
            self.parent().buffer = []

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
        i = 0
        j = len(polygon.points) - 1
        while i < len(polygon.points):
            xi = self.drawer.points_display_table[polygon.points[i]][0]
            yi = self.drawer.points_display_table[polygon.points[i]][1]
            xj = self.drawer.points_display_table[polygon.points[j]][0]
            yj = self.drawer.points_display_table[polygon.points[j]][1]

            intersect = ((yi > y) != (yj > y)) and (
                x < (xj - xi) * (y - yi) / (yj - yi) + xi)
            if (intersect):
                is_inside = not is_inside
            j = i
            i += 1

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
            QtCore.Qt.Key_D: Matrix(3, 3, math.cos(rotate_angle),
                                    -math.sin(rotate_angle), 0,
                                    math.sin(rotate_angle),
                                    math.cos(rotate_angle),
                                    0, 0, 0, 1),
            QtCore.Qt.Key_W: Matrix(3, 3, 1, 0, 0, 0,
                                    math.cos(rotate_angle),
                                    -math.sin(rotate_angle), 0,
                                    math.sin(rotate_angle),
                                    math.cos(rotate_angle)),
            QtCore.Qt.Key_A: Matrix(3, 3, math.cos(-rotate_angle),
                                    -math.sin(-rotate_angle), 0,
                                    math.sin(-rotate_angle),
                                    math.cos(-rotate_angle),
                                    0, 0, 0, 1),
            QtCore.Qt.Key_S: Matrix(3, 3, 1, 0, 0, 0,
                                    math.cos(-rotate_angle),
                                    -math.sin(-rotate_angle), 0,
                                    math.sin(-rotate_angle),
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
            'Red', lambda _: (self.label.drawer.set_style(
                'point color',
                QtCore.Qt.red),
                self.update_display()))
        point_color_action_orange = self.new_action(
            'Orange', lambda _: (self.label.drawer.set_style(
                'point color',
                QtGui.QColor(255, 102, 0)),
                self.update_display()))
        point_color_action_yellow = self.new_action(
            'Yellow', lambda _: (self.label.drawer.set_style(
                'point color',
                QtCore.Qt.yellow),
                self.update_display()))
        line_style_action_solid = self.new_action(
            'Solid', lambda _: (self.label.drawer.set_style(
                'line style',
                QtCore.Qt.SolidLine),
                self.update_display()))
        line_style_action_dash = self.new_action(
            'Dash', lambda _: (self.label.drawer.set_style(
                'line style',
                QtCore.Qt.DashLine),
                self.update_display()))
        line_style_action_dashdot = self.new_action(
            'Dash Dot', lambda _: (self.label.drawer.set_style(
                'line style',
                QtCore.Qt.DashDotLine),
                self.update_display()))
        line_style_action_dashdotdot = self.new_action(
            'Dash Dot Dot', lambda _: (self.label.drawer.set_style(
                'line style',
                QtCore.Qt.DashDotDotLine),
                self.update_display()))
        edit_mode = self.new_action(
            'Edit', lambda _: self.set_mode(Mode.EDIT), shortcut='Q')
        view_mode = self.new_action(
            'View', lambda _: self.set_mode(Mode.VIEW), shortcut='E')
        resize_mode = self.new_action(
            'Resize', lambda _: self.set_mode(Mode.RESIZE), shortcut='R')
        cross_mode = self.new_action(
            'Cross', lambda _: self.set_mode(Mode.CROSS), shortcut='T')
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
        ln_settings_style = ln_settings.addMenu('Style')  # TODO
        ln_settings_style.addAction(line_style_action_solid)
        ln_settings_style.addAction(line_style_action_dash)
        ln_settings_style.addAction(line_style_action_dashdot)
        ln_settings_style.addAction(line_style_action_dashdotdot)
        ln_settings_width = ln_settings.addMenu('Width')  # TODO
        ln_settings_color = ln_settings.addMenu('Color')  # TODO
        pg_settings = settings.addMenu('Polygon')
        pg_settings_border_style = pg_settings.addMenu('Border Style')  # ToDO
        pg_settings_border_color = pg_settings.addMenu('Border Style')  # TODO
        pg_settings_style = pg_settings.addMenu('Style')  # TODO
        pg_settings_color = pg_settings.addMenu('Color')  # TODO
        sp_settings = settings.addMenu('Sphere')
        sp_settings_border_style = sp_settings.addMenu('Border Style')  # ToDO
        sp_settings_border_color = sp_settings.addMenu('Border Style')  # TODO
        sp_settings_style = sp_settings.addMenu('Style')  # TODO
        sp_settings_color = sp_settings.addMenu('Color')  # TODO
        mode_menu = menubar.addMenu('Modes')
        mode_menu.addAction(edit_mode)
        mode_menu.addAction(view_mode)
        mode_menu.addAction(resize_mode)
        mode_menu.addAction(cross_mode)
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
            self.model.add_polygon(self.buffer)
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
            print("not found the file")
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
        except IOError:
            print('save was interrupted')
        self.update_display()

    def screenshot(self, filename):
        filename, ok = QtWidgets.QInputDialog.getText(
            self, 'Filename',
            'Enter the filename to save screen(without extention):')
        if not ok:
            return
        screen = QtWidgets.QApplication.primaryScreen()
        screen.grabWindow(self.winId()).save(filename + '.png', 'png')
