#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI PGAI panel components."""

from __future__ import absolute_import, division, print_function

import sys

import numpy as np
from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, \
    GL_DEPTH_TEST, GL_LINES, GL_MODELVIEW, GL_PROJECTION, GL_SMOOTH, glBegin, \
    glClear, glColor3f, glColor3fv, glEnable, glEnd, glLoadIdentity, \
    glMatrixMode, glPopMatrix, glPushMatrix, glRotatef, glShadeModel, \
    glTranslatef, glVertex3fv, glViewport
from OpenGL.GLU import GLU_LINE, gluCylinder, gluNewQuadric, gluPerspective, \
    gluQuadricDrawStyle
from OpenGL.GLUT import GLUT_DEPTH, GLUT_DOUBLE, GLUT_RGB, glutInit, \
    glutInitDisplayMode, glutSolidCone, glutSolidCube, glutStrokeString, \
    glutWireSphere
# pylint: disable=no-name-in-module
from OpenGL.GLUT.fonts import GLUT_STROKE_MONO_ROMAN

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QDialogButtonBox, QDoubleSpinBox, \
    QFileDialog, QGridLayout, QMessageBox, QScrollBar, QStyledItemDelegate, \
    Qt, QTableWidget, QTableWidgetItem, QWidget, pyqtSignal, pyqtSlot
from nicos.utils import findResource

from nicos_mlz.pgaa.gui.panels.collision import cuboid_values, \
    cylinder_values, sphere_values

try:
    from PyQt5.QtOpenGL import QGLWidget
except ImportError:
    QGLWidget = QWidget


class GLWidget(QGLWidget):
    """Class drawing the max. space and the measurement cells."""

    positions = []
    activeCell = None
    aspect = 1

    sample_diameter = 0.
    sample_height = 0.
    sample_width = 0.
    sample_thickness = 0.
    cl = 3.

    # one of 'cuboid', 'cylinder', 'sphere', 'free input', 'load from file'
    shape = 'cuboid'

    def __init__(self, parent=None):
        QGLWidget.__init__(self, parent)
        self.yRotDeg = 0.0
        self.xRotDeg = 0.0
        self.offsets = [0., -1., 0]

    def initializeGL(self):
        self.qglClearColor(Qt.white)
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGB, GLUT_DOUBLE, GLUT_DEPTH)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height if height else 1)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        self.aspect = width / float(height)
        gluPerspective(45., self.aspect, 1., 100.)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0., 0., -4. / min(self.aspect, 0.7))

        glRotatef(self.yRotDeg, 0., 1., 0.)
        glRotatef(self.xRotDeg, 1., 0., 0.)

        if self.shape == 'cuboid':
            self.paintCuboid(self.sample_width, self.sample_thickness,
                             self.sample_height, rotate=45.)
        elif self.shape == 'cylinder':
            self.paintCylinder(self.sample_diameter, self.sample_height)
        elif self.shape == 'sphere':
            self.paintSphere(self.sample_diameter)
        else:
            self.sample_width = self.sample_thickness = 70
            self.sample_height = 100
            self.paintCuboid(self.sample_width, self.sample_thickness,
                             self.sample_height)

        self.paintArrow('x', [0, 0, 1])
        self.paintArrow('y', [1, 0, 0])
        self.paintArrow('z', [0, 1, 0])
        self.paintArrow('n', [0, 0, 0])
        self.paintArrow('gamma', [1, 0, 1])

        self.paintCells()

    def paintCells(self):
        size = 0.0855 * self.cl / 3.
        for i, p in enumerate(self.positions):
            color = (1., 0., 0.) if i == self.activeCell else (0., 0., 1.)
            glColor3fv(color)
            glPushMatrix()
            offs = np.array([p[0], p[2], p[1]]) / 35. + self.offsets
            glTranslatef(offs[0], offs[1], offs[2])
            glutSolidCube(size)
            glPopMatrix()

    def paintCuboid(self, width, thickness, height, rotate=0.):
        verticies = np.array([
            (1., -1., -1.),
            (1., 1., -1.),
            (-1., 1., -1.),
            (-1., -1., -1.),
            (1., -1., 1.),
            (1., 1., 1.),
            (-1., -1., 1.),
            (-1., 1., 1.),
        ])
        edges = [
            (0, 1),
            (0, 3),
            (0, 4),
            (2, 1),
            (2, 3),
            (2, 7),
            (6, 3),
            (6, 4),
            (6, 7),
            (5, 1),
            (5, 4),
            (5, 7),
        ]

        scale = np.array([width, height, thickness]) / 70.

        glColor3f(0., 0., 0.)
        glPushMatrix()
        glTranslatef(0., scale[1] - 1., 0.)  # move down
        glRotatef(rotate, 0., 1., 0)
        glBegin(GL_LINES)
        for edge in edges:
            for vertex in edge:
                glVertex3fv(verticies[vertex] * scale)
        glEnd()
        glPopMatrix()

    def paintCylinder(self, diameter, height):
        r = diameter / 70.
        height = 2 * height / 70.
        glColor3f(0., 0., 0.)
        glPushMatrix()
        glTranslatef(*self.offsets)  # move down
        glRotatef(-90., 1., 0., 0.)
        quadric = gluNewQuadric()
        gluQuadricDrawStyle(quadric, GLU_LINE)
        slices = max(int(round(r * 32)), 15)
        gluCylinder(quadric, r, r, height, slices, 1)
        glPopMatrix()

    def paintSphere(self, diameter):
        r = diameter / 70.
        glColor3f(0., 0., 0.)
        glPushMatrix()
        glTranslatef(0., r - 1., 0.)  # move down
        glRotatef(90., 1., 0., 0.)
        slices = max(int(round(r * 32)), 9)
        glutWireSphere(r, slices, slices)
        glPopMatrix()

    def paintText(self, text):
        glPushMatrix()
        glColor3fv((0., 0., 0.))
        glutStrokeString(GLUT_STROKE_MONO_ROMAN, text)
        glPopMatrix()

    def paintArrow(self, direction, color):
        d = 0.01
        length = 0.5
        glPushMatrix()
        glColor3fv(color)
        if direction == 'n':
            glTranslatef(0., -1.1, 2.)
        elif direction == 'gamma':
            glTranslatef(1.2, -1.1, 0.)
        else:
            glTranslatef(-1., -1., 1.)
        quadric = gluNewQuadric()
        if direction in ('x', 'gamma'):
            glRotatef(90., 0., 1., 0.)
        elif direction == 'y':
            glRotatef(90, -1., 0., 0.)
        elif direction in ('z', 'n'):
            glRotatef(180, -1, 0, 0)
        gluCylinder(quadric, d, d, length, 48, 48)
        glTranslatef(0, 0, length)
        glutSolidCone(2. * d, 0.1, 48, 48)
        glPopMatrix()

    @pyqtSlot(int, int)
    def positionActivated(self, row, column):
        self.activeCell = row
        self.update()

    @pyqtSlot(int)
    def rotateX(self, x):
        self.xRotDeg = x
        self.update()

    @pyqtSlot(int)
    def rotateY(self, y):
        self.yRotDeg = y
        self.update()

    @pyqtSlot(float, float, float)
    def pointAdded(self, x, y, z):
        self.positions.append([x, y, z])
        self.update()

    @pyqtSlot(int, int, float)
    def pointModified(self, row, col, val):
        self.positions[row][col] = val
        self.update()

    @pyqtSlot(int)
    def pointRemove(self, row):
        self.positions.pop(row)
        self.update()

    @pyqtSlot(str)
    def sampleShapeChanged(self, shape):
        self.shape = shape
        self.update()

    @pyqtSlot(float)
    def dim1Changed(self, value):
        self.sample_width = value
        self.sample_diameter = value
        self.update()

    @pyqtSlot(float)
    def dim2Changed(self, value):
        if self.shape in ('cuboid', 'cylinder'):
            self.sample_height = value
            self.update()

    @pyqtSlot(float)
    def dim3Changed(self, value):
        if self.shape == 'cuboid':
            self.sample_thickness = value
            self.update()

    @pyqtSlot(float)
    def cubeSizeChanged(self, value):
        self.cl = value


class PGAIWidget(QWidget):
    """Widget to rotate the measurement cells and space cell."""

    maxrot = 95

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.gridLayout = QGridLayout(self)
        self.widget = GLWidget(self)
        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)

        self.verticalScrollBar = QScrollBar(self)
        self.verticalScrollBar.setOrientation(Qt.Vertical)
        self.verticalScrollBar.setMinimum(-self.maxrot)
        self.verticalScrollBar.setMaximum(self.maxrot)
        self.verticalScrollBar.setValue(0)

        self.gridLayout.addWidget(self.verticalScrollBar, 0, 1, 1, 1)

        self.horizontalScrollBar = QScrollBar(self)
        self.horizontalScrollBar.setOrientation(Qt.Horizontal)
        self.horizontalScrollBar.setMinimum(-self.maxrot)
        self.horizontalScrollBar.setMaximum(self.maxrot)

        self.gridLayout.addWidget(self.horizontalScrollBar, 1, 0, 1, 1)
        self.verticalScrollBar.valueChanged.connect(self.widget.rotateX)
        self.horizontalScrollBar.valueChanged.connect(self.widget.rotateY)
        self.horizontalScrollBar.setValue(20)


class PositionSpinBox(QDoubleSpinBox):
    """Specific spin box implementation.

    Limited range, defined unit, number of decimals and accelerated.
    """

    def __init__(self, minval=0, maxval=100, parent=None):
        QDoubleSpinBox.__init__(self, parent)
        self.setAccelerated(True)
        self.setDecimals(2)
        self.setSuffix(' mm')
        self.setMinimum(minval)
        self.setMaximum(maxval)
        p = parent
        while p and not isinstance(p, QTableWidget):
            p = p.parent()
        self.p = p
        self.valueChanged.connect(self.cellValueChanged)

    @pyqtSlot(float)
    def cellValueChanged(self, val):
        item = self.p.currentItem()
        self.p.valueChanged.emit(item.row(), item.column(), val)


class PositionDelegate(QStyledItemDelegate):
    """Specific table editor delegate."""

    def createEditor(self, parent, option, index):
        w = PositionSpinBox(0 if index.column() == 2 else -35.,
                            100 if index.column() == 2 else 35, parent)
        return w

    def setEditorData(self, editor, index):
        value = float(index.model().data(index, Qt.EditRole))
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        editor.interpretText()
        value = editor.value()
        model.setData(index, value, Qt.EditRole)


class PositionTable(QTableWidget):
    """Display all selected measurement positions.

    Each value is modifiable and removable.
    """

    pointRemove = pyqtSignal(int)
    valueChanged = pyqtSignal(int, int, float)

    def __init__(self, parent=None):
        QTableWidget.__init__(self, parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            item = self.itemAt(event.pos())
            if item:
                if QMessageBox.question(self, 'Remove data point', 'Do you '
                                        'really want to remove this data '
                                        'point?') == QMessageBox.Yes:
                    event.accept()
                    r = item.row()
                    self.removeRow(r)
                    self.pointRemove.emit(r)
        QTableWidget.mousePressEvent(self, event)

    def clearTable(self):
        while self.rowCount():
            self.removeRow(0)
            self.pointRemove.emit(0)

    def getValues(self, row):
        return [float(self.item(row, i).text()) for i in range(3)]


class PGAIPanel(Panel):
    """PGAI specific panel.

    Displays the measurement positions in a measurement cell, and in a table.
    """

    panelName = 'PGAI'

    pointAdded = pyqtSignal(float, float, float)
    pointModified = pyqtSignal(int, int, float)

    current_status = None

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_mlz/pgaa/gui/panels/pgai.ui'))
        w = self.widget.widget
        self.pointAdded.connect(w.pointAdded)
        self.pointTable.cellActivated.connect(w.positionActivated)
        self.pointTable.cellClicked.connect(w.positionActivated)
        self.pointTable.cellEntered.connect(w.positionActivated)
        self.pointTable.cellPressed.connect(w.positionActivated)
        self.pointTable.verticalHeader().sectionClicked.connect(
            lambda row: w.positionActivated(row, 0))
        self.newPointButton.clicked.connect(self.newPoint)
        self.buttonBox.button(QDialogButtonBox.SaveAll).setText('Run')
        self.pointTable.itemChanged.connect(self.modifyPoint)
        self.pointModified.connect(w.pointModified)
        self.pointTable.setItemDelegate(PositionDelegate())
        self.pointTable.pointRemove.connect(w.pointRemove)
        self.buttonBox.accepted.connect(self.runScript)
        self.pointTable.valueChanged.connect(self.cellValueModified)
        self.sampleShape.currentIndexChanged[str].connect(w.sampleShapeChanged)
        self.sampleShape.currentIndexChanged[str].connect(
            self.sampleShapeChanged)
        self.dimValue1.valueChanged.connect(w.dim1Changed)
        self.dimValue2.valueChanged.connect(w.dim2Changed)
        self.dimValue3.valueChanged.connect(w.dim3Changed)

        self.dimValue1.valueChanged.connect(self.sampleSizeChanged)
        self.dimValue2.valueChanged.connect(self.sampleSizeChanged)
        self.dimValue3.valueChanged.connect(self.sampleSizeChanged)

        self.volumeSize.valueChanged.connect(self.sampleSizeChanged)
        self.volumeSize.valueChanged.connect(w.cubeSizeChanged)
        self.volumeDistance.valueChanged.connect(self.sampleSizeChanged)
        self.pointTable.horizontalHeader().sectionClicked.connect(
            self.sortOrderChanged)

        w.dim1Changed(self.dimValue1.value())
        w.dim2Changed(self.dimValue2.value())
        w.dim3Changed(self.dimValue3.value())

        self.fileName.hide()
        self.fileNameSelect.hide()
        self.fileName.editingFinished.connect(self.loadPointsFromFile)
        self.fileNameSelect.clicked.connect(self.selectFileName)

        self.sampleShapeChanged(self.sampleShape.currentText())

    @pyqtSlot()
    def sampleSizeChanged(self):
        self.sampleShapeChanged(self.sampleShape.currentText())

    @pyqtSlot(int)
    def sortOrderChanged(self, item):
        for _ in range(self.pointTable.rowCount()):
            self.widget.widget.pointRemove(0)
        for i in range(self.pointTable.rowCount()):
            self.pointAdded.emit(*self.pointTable.getValues(i))

    def _init_cuboid(self):
        self.pointTable.clearTable()
        width = self.dimValue1.value()
        height = self.dimValue2.value()
        thickness = self.dimValue3.value()
        cl = self.volumeSize.value()
        space = self.volumeDistance.value()

        w = self.widget.widget
        w.dim1Changed(width)
        w.dim2Changed(height)
        w.dim3Changed(thickness)
        for p in cuboid_values(width, thickness, height, 45, cl, space):
            self.addPoint(*p)

    def _init_cylinder(self):
        self.pointTable.clearTable()
        radius = self.dimValue1.value() / 2.
        height = self.dimValue2.value()
        cl = self.volumeSize.value()
        space = self.volumeDistance.value()

        w = self.widget.widget
        w.dim1Changed(2 * radius)
        w.dim2Changed(height)
        for p in cylinder_values(radius, height, cl, space):
            self.addPoint(*p)

    def _init_sphere(self):
        self.pointTable.clearTable()

        radius = self.dimValue1.value() / 2.
        cl = self.volumeSize.value()
        space = self.volumeDistance.value()
        w = self.widget.widget
        w.dim1Changed(2 * radius)
        for p in sphere_values(radius, cl, space):
            self.addPoint(*p)

    def _init_free(self):
        self.pointTable.clearTable()

    def _init_file(self):
        self.pointTable.clearTable()
        fn = self.fileName.text()
        if fn:
            try:
                with open(fn, 'r') as f:
                    for line in f.readlines():
                        x, y, z = line.split(',')
                        self.addPoint(float(x), float(y), float(z))
            except IOError:
                self.fileName.setText('')

    def addPoint(self, x, y, z):
        row = self.pointTable.rowCount()
        self.pointTable.setRowCount(row + 1)

        item = self._create_table_widget(x)
        item.setBackground(Qt.blue)
        item.setForeground(Qt.white)
        self.pointTable.setItem(row, 0, item)

        item = self._create_table_widget(y)
        item.setBackground(Qt.green)
        self.pointTable.setItem(row, 1, item)

        item = self._create_table_widget(z)
        item.setBackground(Qt.red)
        item.setForeground(Qt.white)
        self.pointTable.setItem(row, 2, item)

        self.pointAdded.emit(x, y, z)

    def _create_table_widget(self, value):
        return QTableWidgetItem('%s' % value)

    def updateStatus(self, status, exception=False):
        self.current_status = status

    @pyqtSlot()
    def selectFileName(self):
        fn, _ = QFileDialog.getOpenFileName(self, 'Load data points')
        if fn:
            self.fileName.setText(fn)
            self.fileName.editingFinished.emit()

    @pyqtSlot()
    def loadPointsFromFile(self):
        self._init_file()

    @pyqtSlot(QTableWidgetItem)
    def modifyPoint(self, item):
        if item.isSelected():
            self.pointModified.emit(item.row(), item.column(),
                                    float(item.text()))

    @pyqtSlot(int, int, float)
    def cellValueModified(self, row, col, val):
        self.pointModified.emit(row, col, val)

    @pyqtSlot()
    def newPoint(self):
        self.addPoint(self.newPointX.value(), self.newPointY.value(),
                      self.newPointZ.value())

    @pyqtSlot(str)
    def sampleShapeChanged(self, shape):
        for w in (self.dimLabel1, self.dimValue1,
                  self.dimLabel2, self.dimValue2,
                  self.dimLabel3, self.dimValue3,
                  self.fileName, self.fileNameSelect,
                  self.lblSampleDimension, self.lblMeasurementVolume,
                  self.volumeDistance, self.lblVolumeDistance):
            w.hide()
        if shape == 'cuboid':
            self._init_cuboid()
            self.dimLabel1.setText('Width (X)')
            self.dimLabel2.setText('Height (Y)')
            self.dimLabel3.setText('Thickness (Z)')
            for w in (self.dimLabel1, self.dimValue1,
                      self.dimLabel2, self.dimValue2,
                      self.dimLabel3, self.dimValue3,
                      self.lblSampleDimension, self.lblMeasurementVolume,
                      self.volumeDistance, self.lblVolumeDistance):
                w.show()
        elif shape == 'cylinder':
            self._init_cylinder()
            self.dimLabel1.setText('Diameter')
            self.dimLabel2.setText('Height')
            for w in (self.dimLabel1, self.dimValue1,
                      self.dimLabel2, self.dimValue2,
                      self.lblSampleDimension, self.lblMeasurementVolume,
                      self.volumeDistance, self.lblVolumeDistance):
                w.show()
        elif shape == 'sphere':
            self._init_sphere()
            self.dimLabel1.setText('Diameter')
            for w in (self.dimLabel1, self.dimValue1,
                      self.lblSampleDimension, self.lblMeasurementVolume,
                      self.volumeDistance, self.lblVolumeDistance):
                w.show()
        elif shape == 'free input':
            self._init_free()
        elif shape == 'load from file':
            self._init_file()
            for w in (self.fileName, self.fileNameSelect):
                w.show()

    @pyqtSlot()
    def runScript(self):
        template = """
w = 45
for xt, yt, zt in %(positions)s:
    print('recording %%.2f, %%.2f, %%.2f' %% (xt, yt, zt))
    # info_string = 'D%%dC%%dR%%d' %% (t, col, row)
    info_string = ''
    file_string = '_x_%%.2f_y_%%.2f_z_%%.2f_w_%%.0f' %% (xt, yt, zt, w)
    x.move(xt)
    y.move(yt)
    z.move(zt)
    wait(x, y, z)
    shutter.maw('%(shutter)s')
    count(info_string, LiveTime=%(time)f, Filename=file_string)
    shutter.maw('closed')
    print('spectra recorded and written to %%s' %% file_string)
"""
        positions = [[float(self.pointTable.item(r, 0).text()),
                      float(self.pointTable.item(r, 1).text()),
                      float(self.pointTable.item(r, 2).text())]
                     for r in range(self.pointTable.rowCount())]
        script = template % {'positions': positions,
                             'shutter': self.shutter.value(),
                             'time': self.livetime.value()}
        self.client.run(script)
        self.pointTable.clearTable()
