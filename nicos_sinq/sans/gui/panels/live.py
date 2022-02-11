# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

from os import path
from types import MethodType as createBoundMethod

import numpy as np
from polarTransform import convertToPolarImage
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QDialog
from scipy import ndimage

from nicos.clients.flowui.panels.live import LiveDataPanel as EssLiveDataPanel
from nicos.clients.gui.main import log
from nicos.clients.gui.utils import loadUi

from nicos_sinq.sans.gui import uipath

TWO_PI = 2 * np.pi
MAX_ANGLE_SIZE = 100


class SetCenterDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        loadUi(self, path.abspath(path.join(path.sep,
                                            *parent.ui.split('/')[:-1],
                                            'set_center.ui')))
        self.XcEdit.setValidator(QIntValidator(0, 999999))
        self.YcEdit.setValidator(QIntValidator(0, 999999))

    def getCenter(self):
        x, y = self.XcEdit.text() or '0', self.YcEdit.text() or '0'
        return int(x), int(y)


def to_polar_image(cartesian_image, center=None, final_angle=TWO_PI):
    image = cartesian_image  # or ROI

    def is_valid(_center):
        # discard meaningless value
        if not all(2 < c <= high-2 for c, high in zip(_center,
                                                       cartesian_image.shape)):
            return False
        return True

    if not center or not is_valid(center):
        center = ndimage.measurements.center_of_mass(image)
    angle_size = min(MAX_ANGLE_SIZE, min(cartesian_image.shape))
    final_radius = int(
        min([center[0], cartesian_image.shape[0] - center[0], center[1],
             cartesian_image.shape[1] - center[1]]))
    if final_radius == 0:
        raise ValueError('final_radius=0, check center position')
    polar_image, _ = convertToPolarImage(cartesian_image, center=center,
                                         finalRadius=final_radius,
                                         finalAngle=final_angle,
                                         radiusSize=final_radius,
                                         angleSize=angle_size)
    polar_labels = {
        'x': np.linspace(0, final_radius, final_radius),
        'y': np.linspace(0, final_angle, angle_size)
        }

    return polar_image, polar_labels


# use log(1+data) instead of log(data)
def updateZData(target):
    arr = target._arrays[0].ravel()
    if target._logscale:
        arr = np.ma.log10(1 + arr).filled(-1)

    # TODO: implement 'sliders' for amin, amax
    amin, amax = arr.min(), arr.max()

    if amin != amax:
        target.surf.z = 1000 + 255 / (amax - amin) * (arr - amin)
    elif amax > 0:
        target.surf.z = 1000 + 255 / amax * arr
    else:
        target.surf.z = 1000 + arr


class SansLiveDataPanel(EssLiveDataPanel):
    """
    Extends the EssLiveDataPanel with a button to convert the plot in polar
    plot (and back) and log scale in the form `log(1+x)`
    """

    ui = path.join(uipath, 'panels', 'ui_files', 'live.ui')

    def __init__(self, parent, client, options):
        EssLiveDataPanel.__init__(self, parent, client, options)
        self.dlg = SetCenterDialog(self)
        self.dlg.hide()

    def createPanelToolbar(self):
        toolbar = EssLiveDataPanel.createPanelToolbar(self)
        toolbar.addAction(self.actionPolar)
        toolbar.addAction(self.actionSetCenter)
        return toolbar

    def initLiveWidget(self, widgetcls):
        EssLiveDataPanel.initLiveWidget(self, widgetcls)
        self.widget.gr.keepRatio = True
        self.widget.updateZData = createBoundMethod(updateZData, self.widget)

    def _show(self, data=None):
        """Show the provided data. If no data has been provided extract it
        from the datacache via the current item's uid.

        :param data: dictionary containing 'dataarrays' and 'labels'
        """
        idx = self.fileList.currentRow()
        if idx == -1:
            self.fileList.setCurrentRow(0)
            return

        # no data has been provided, try to get it from the cache
        if data is None:
            data = self.getDataFromItem(self.fileList.currentItem())
            # still no data
            if data is None:
                return

        arrays = data.get('dataarrays', [])
        labels = data.get('labels', {})
        titles = data.get('titles', {})
        try:
            if self.actionPolar.isChecked():
                # make sure that the certer is meanungful
                output = [to_polar_image(np.array(array),
                                         center=self.dlg.getCenter()) for array
                    in arrays]
                labels = output[0][1]
                arrays = [val[0] for val in output]
                titles = {'x': 'rho', 'y': 'theta'}
        except ValueError as e:
            log.error(e)
            return

        # if multiple datasets have to be displayed in one widget, they have
        # the same dimensions, so we only need the dimensions of one set
        self._initLiveWidget(arrays[0])
        self.applyPlotSettings()
        for widget in self._get_all_widgets():
            widget.setData(arrays, labels)
            widget.setTitles(titles)

        if self.unzoom and self.widget:
            self.on_actionUnzoom_triggered()

    @pyqtSlot()
    def on_actionPolar_triggered(self):
        self._show()

    @pyqtSlot()
    def on_actionSetCenter_triggered(self):
        self.dlg.show()
