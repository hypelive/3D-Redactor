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

        self.last_x = None
        self.last_y = None
        self.last_time_clicked = time.time()
        self.forget_object_delay = 0.15
        self.object_to_interact = None

        self.drawer = None
        self.style_preset = 81

    def update_scene_display(self):
        with self.get_painter() as painter:
            painter.fillRect(
                0, 0, RESOLUTION[0], RESOLUTION[1], QtGui.QGradient.Preset(self.style_preset))

            if self.parent().display_axiss:
                self.drawer.draw_coordinates_system(
                    self.parent().split_coordinates, self.parent().axiss_width,
                    self.parent().axiss_size, painter)

            for obj in self.parent().model.objects:
                self.drawer.paint_object(
                    obj, self.parent().split_coordinates, painter)
            # can we do mode description?... hmmm
            painter.drawText(
                20, 40, f"selected mode: {str(self.parent().mode)}")

    def get_painter(self):
        painter = QtGui.QPainter(self.pixmap())
        painter.setPen(QtGui.QPen(QtGui.QColor(
            255, 102, 0), 5, QtCore.Qt.SolidLine))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 102, 70)))
        return painter

    def mousePressEvent(self, event):
        if self.parent().mode == Mode.POINT:
            self.set_point(event)
        elif self.parent().mode == Mode.LINE:
            self.choose_line_points(event)
        elif self.parent().mode == Mode.POLYGON:
            self.choose_polygon_points(event)
        elif self.parent().mode == Mode.SPHERE:
            self.set_sphere(event)

        self.object_to_interact = None
        self.refresh_interaction_variables(event)
        self.parent().update_display()

    def refresh_interaction_variables(self, event):
        self.last_x = event.x()
        self.last_y = event.y()
        self.last_time_clicked = time.time()

    def set_point(self, event):
        self.parent().model.add_point((self.parent().model.display_plate_basis[0] * (event.x() - self.parent().split_coordinates[0])) +
                                      (self.parent(
                                      ).model.display_plate_basis[1] * (event.y() - self.parent().split_coordinates[1])))

    def set_sphere(self, event):
        self.parent().model.add_sphere((self.parent().model.display_plate_basis[0] * (event.x() - self.parent().split_coordinates[0])) +
                                       (self.parent(
                                       ).model.display_plate_basis[1] * (event.y() - self.parent().split_coordinates[1])))

    def choose_line_points(self, event):
        self.update_object_to_interact(event)
        if self.object_to_interact and isinstance(self.object_to_interact, Point):
            self.parent().point_buffer.append(self.object_to_interact)
        if len(self.parent().point_buffer) == 2:
            self.parent().model.add_line(self.parent().point_buffer[0],
                                         self.parent().point_buffer[1])
            self.parent().mode = Mode.VIEW
            self.parent().point_buffer = []

    def choose_polygon_points(self, event):
        self.update_object_to_interact(event)
        if self.object_to_interact and isinstance(self.object_to_interact, Point):
            self.parent().point_buffer.append(self.object_to_interact)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self.parent().mode == Mode.VIEW:
            self.parent().split_coordinates[0] += event.x() - self.last_x
            self.parent().split_coordinates[1] += event.y() - self.last_y
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
                (event.x() - self.last_x) +
                self.parent().model.display_plate_basis[1]
                * (event.y() - self.last_y))
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
        return self.get_distance(event.x(), event.y(),
                                 *self.drawer.points_display_table[sphere.point])

    def get_distance_to_line(self, event, line):
        return (self.get_distance_to_point(event, line.start) + self.get_distance_to_point(event, line.end) -
                self.get_distance(*self.drawer.points_display_table[line.start], *self.drawer.points_display_table[line.end]))

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

        self.split_coordinates = [640, 360]
        self.axiss_size = 50
        self.axiss_width = 3
        self.point_buffer = []

        self.drawer = None

        self.modes = {
            QtCore.Qt.Key_Q: Mode.EDIT,
            QtCore.Qt.Key_E: Mode.VIEW,
            QtCore.Qt.Key_R: Mode.RESIZE,
            QtCore.Qt.Key_L: Mode.LINE,
            QtCore.Qt.Key_P: Mode.POLYGON}

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
#
#        new_scene_action = QtWidgets.QAction(
#            QtGui.QIcon('textures/new.png'), 'New', self)
#        new_scene_action.triggered.connect(self.init_new_model)
#        save_action = QtWidgets.QAction(
#            QtGui.QIcon('textures/save.png'), 'Save', self)
#        save_action.triggered.connect(self.save_model)
#        open_action = QtWidgets.QAction(
#            QtGui.QIcon('textures/open.png'), 'Open', self)
#        open_action.triggered.connect(self.open_model)
#        menubar = self.menuBar()
#        menubar.setStyleSheet("""QMenuBar {
#         background-color: rgb(220,150,120);
#        }
#
#     QMenuBar::item {
#         background: rgb(220,150,120);
#     }""")
#        fileMenu = menubar.addMenu('Files')  # menu
#        fileMenu.addAction(new_scene_action)
#        fileMenu.addAction(save_action)
#        fileMenu.addAction(open_action)
#        fileMenu = menubar.addMenu('Modes')
#
        self.label = SceneWindow(self)
        self.setCentralWidget(self.label)

        but = QtWidgets.QPushButton('Pt', self)  # vinesti v method
        but.setGeometry(20, 60, 40, 30)
        but.clicked.connect(lambda _: self.set_mode(Mode.POINT))
        but.setIcon(QtGui.QIcon('textures/pt.png'))
        but.setIconSize(QtCore.QSize(20, 15))

        but = QtWidgets.QPushButton('Ln', self)
        but.setGeometry(20, 100, 40, 30)
        but.clicked.connect(lambda _: self.set_mode(Mode.LINE))
        but.setIcon(QtGui.QIcon('textures/ln.png'))
        but.setIconSize(QtCore.QSize(30, 15))

        but = QtWidgets.QPushButton('Pg', self)
        but.setGeometry(20, 140, 40, 30)
        but.clicked.connect(lambda _: self.set_mode(Mode.POLYGON))
        but.setIcon(QtGui.QIcon('textures/plg.png'))
        but.setIconSize(QtCore.QSize(20, 15))

        but = QtWidgets.QPushButton('Sp', self)
        but.setGeometry(20, 180, 40, 30)
        but.clicked.connect(lambda _: self.set_mode(Mode.SPHERE))
        but.setIcon(QtGui.QIcon('textures/sp.png'))
        but.setIconSize(QtCore.QSize(25, 17))

        but = QtWidgets.QPushButton('scr', self)
        but.setGeometry(15, 600, 65, 20)
        but.clicked.connect(self.screenshot)
        but.setIcon(QtGui.QIcon('textures/camera.png'))
        but.setIconSize(QtCore.QSize(30, 20))

        but = QtWidgets.QPushButton('save', self)
        but.setGeometry(50, 600, 65, 20)
        but.clicked.connect(self.save_model)
        but.setIcon(QtGui.QIcon('textures/camera.png'))
        but.setIconSize(QtCore.QSize(30, 20))

        but = QtWidgets.QPushButton('open', self)
        but.setGeometry(140, 600, 65, 20)
        but.clicked.connect(self.open_model)
        but.setIcon(QtGui.QIcon('textures/camera.png'))
        but.setIconSize(QtCore.QSize(30, 20))

    def update_display(self):
        self.label.update_scene_display()
        self.update()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if not self.model:
            return
        if event.key() == QtCore.Qt.Key_CapsLock:
            self.display_axiss = not self.display_axiss
        elif event.key() in self.modes:  # if we change when polygon - end pg
            if self.mode == Mode.POLYGON and len(self.point_buffer) > 2:
                self.model.add_polygon(self.point_buffer)
                self.point_buffer = []
            self.mode = self.modes[event.key()]
            self.point_buffer = []
        elif event.key() in self.rotate:
            self.model.update_display_matrix(self.rotate[event.key()])
        self.update_display()

    def set_mode(self, mode: Mode):  # mode change will ve lambda
        self.mode = mode
        self.update_display()

    def init_new_model(self):
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
