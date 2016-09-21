#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Dialogs for the "Measurement" commandlet."""

import itertools
from collections import OrderedDict

from PyQt4.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt4.QtGui import QDialog, QListWidgetItem, QTableWidgetItem, QLabel, \
    QVBoxLayout, QFrame, QWidget, QTableWidgetSelectionRange, QFileDialog

from nicos.clients.gui.utils import loadUi, DlgUtils
from nicos.guisupport.utils import DoubleValidator
from nicos.utils import findResource, formatDuration
from nicos.kws1.gui.measelement import Selector, Detector, Chopper, Lenses, \
    Polarizer, Collimation, MeasTime, Sample, Device
from nicos.kws1.gui.sampleconf import parse_sampleconf


SAMPLES = 'samples'
DETSETS = 'detector/collimation'
DEVICES = 'other devices'

LOOPS = [
    SAMPLES,
    DETSETS,
    DEVICES,
]

SAMPLE_NUM = 32


class MeasDef(object):
    def __init__(self, rtmode):
        self.rtmode = rtmode
        self.loops = LOOPS[:]
        self.samples = []
        self.detsets = []
        self.devices = []
        self.samplefile = None

    def getElements(self):
        elements = [
            ('selector', Selector),
            ('detector', Detector),
            ('collimation', Collimation),
            ('polarizer', Polarizer),
            ('lenses', Lenses),
        ]
        if not self.rtmode:
            elements.insert(2, ('chopper', Chopper))  # before collimation
            elements.append(('time', MeasTime))
        return elements

    def getEntries(self, loop):
        if loop == SAMPLES:
            return self.samples
        elif loop == DETSETS:
            return self.detsets
        elif loop == DEVICES:
            return self.devices

    def getTable(self):
        # this is a list of list of dicts:
        # [[A1, A2, ...], [B1, ...], [C1, ...], ...]
        # where An, Bn, Cn are OrderedDicts with keyword=value for kwscount
        dict_lists = self.getEntries(self.loops[0]) + \
            self.getEntries(self.loops[1]) + \
            self.getEntries(self.loops[2])
        # if there are no settings at all, we have no entries
        if not dict_lists:
            return []
        # now we have to create the cartesian product of all of those lists,
        # and merge the ordered dicts for each element
        result = []
        for dicts in itertools.product(*dict_lists):
            entry = OrderedDict()
            for d in sorted(dicts, key=lambda d: d.values()[0].ORDER):
                entry.update(d)
            result.append(entry)
        # post-process sample measurement time factor
        for entry in result:
            if 'sample' in entry and 'time' in entry:
                entry['time'] = new_time = \
                    MeasTime('time', None, entry['time'].getValue())
                new_time.value *= entry['sample'].extra[1]
        return result


class SampleDialog(DlgUtils, QDialog):

    def __init__(self, parent, measdef, client):
        self.measdef = measdef
        self.samplefile = None
        self.client = client
        DlgUtils.__init__(self, 'Sample selection')
        QDialog.__init__(self, parent)
        loadUi(self, findResource('custom/kws1/lib/gui/samples.ui'))

        self._init_samplefile = False
        self.samplefile = measdef.samplefile
        if self.samplefile is not None:
            self._init_samplefile = True
            self.on_sampleFileBtn_toggled(True)
            self._init_samplefile = False
        else:
            self.on_currentSamplesBtn_toggled(True)

        if self.measdef.samples:
            for sam in self.measdef.samples[0]:
                newitem = QListWidgetItem(sam['sample'].getValue(),
                                          self.selList)
                newitem.setData(SAMPLE_NUM, sam['sample'].extra[0])
                self._selected.add(sam['sample'].extra[0])

    def _reinit(self, sampleconfigs):
        self.selList.clear()
        self.allList.clear()
        self._selected = set()
        self._times = {}

        for number, sample in sampleconfigs.items():
            item = QListWidgetItem(sample['name'], self.allList)
            item.setData(SAMPLE_NUM, number)
            self._times[number] = sample.get('timefactor', 1.0)

    def toDefs(self):
        results = []
        for item in self.selList.findItems('', Qt.MatchContains):
            num = item.data(SAMPLE_NUM)
            results.append(OrderedDict(sample=Sample(
                'sample', self.client, item.text(),
                extra=(num, self._times.get(num, 1.0)))))
        return [results]

    def on_sampleFileBtn_toggled(self, on):
        if not on:
            return
        if not self._init_samplefile:
            initialdir = self.client.eval('session.experiment.scriptpath', '')
            fn = QFileDialog.getOpenFileName(self, 'Open sample file',
                                             initialdir, 'Sample files (*.py)')
            if not fn:
                self.currentSamplesBtn.setChecked(True)
                return
        else:
            fn = self.samplefile
        try:
            configs = parse_sampleconf(fn)
        except Exception as err:
            self.showError('Could not read file: %s\n\n'
                           'Are you sure this is a sample file?' % err)
            self.currentSamplesBtn.setChecked(True)
            return
        self.samplefile = fn
        self.sampleFileLbl.setText(fn)
        self.sampleFileBtn.setChecked(True)
        self._reinit(dict(enumerate(configs)))

    @pyqtSlot()
    def on_fileSelectBtn_clicked(self):
        if self.sampleFileBtn.isChecked():
            self.on_sampleFileBtn_toggled(True)
        else:
            self.sampleFileBtn.setChecked(True)

    def on_currentSamplesBtn_toggled(self, on):
        if not on:
            return
        self.samplefile = None
        self._reinit(self.client.eval('Exp.samples', None) or {})

    @pyqtSlot()
    def on_rightBtn_clicked(self):
        for item in self.allList.selectedItems():
            if item.data(SAMPLE_NUM) not in self._selected:
                newitem = QListWidgetItem(item.text(), self.selList)
                newitem.setData(SAMPLE_NUM, item.data(SAMPLE_NUM))
                self._selected.add(item.data(SAMPLE_NUM))

    @pyqtSlot()
    def on_leftBtn_clicked(self):
        for item in self.selList.selectedItems():
            self.selList.takeItem(self.selList.row(item))
            self._selected.remove(item.data(SAMPLE_NUM))

    @pyqtSlot()
    def on_clearBtn_clicked(self):
        self.selList.clear()
        self._selected.clear()

    @pyqtSlot()
    def on_upBtn_clicked(self):
        ix = map(self.selList.row, self.selList.selectedItems())
        if not ix or ix[0] == 0:
            return
        self.selList.insertItem(ix[0] - 1, self.selList.takeItem(ix[0]))
        self.selList.setCurrentRow(ix[0] - 1)

    @pyqtSlot()
    def on_downBtn_clicked(self):
        ix = map(self.selList.row, self.selList.selectedItems())
        if not ix or ix[0] == self.selList.count() - 1:
            return
        self.selList.insertItem(ix[0] + 1, self.selList.takeItem(ix[0]))
        self.selList.setCurrentRow(ix[0] + 1)


class DetsetDialog(QDialog):

    def __init__(self, parent, measdef, client):
        self._edit = None
        self.measdef = measdef
        self.client = client
        QDialog.__init__(self, parent)
        loadUi(self, findResource('custom/kws1/lib/gui/detsets.ui'))
        self.table.setColumnCount(len(measdef.getElements()))

        # apply current settings
        self._rows = []
        if measdef.detsets:
            for row in measdef.detsets[0]:
                self.addRow(row)

        # create widgets for new setting
        self._new_elements = {}
        headers = []
        for i, (eltype, cls) in enumerate(measdef.getElements()):
            element = self._new_elements[eltype] = cls(eltype, self.client)
            w = element.createWidget(self, self.client)
            for other in self._new_elements.values():
                if other is not element:
                    element.otherChanged(other.eltype, other.getValue())

            def handler(new_value, eltype=eltype):
                for other in self._new_elements.values():
                    other.otherChanged(eltype, new_value)
            element.changed.connect(handler)
            headers.append(element.getLabel())
            layout = QVBoxLayout()
            layout.addWidget(QLabel(headers[-1], self))
            layout.addWidget(w)
            self.widgetFrame.layout().insertLayout(i, layout)

        # update table widget
        self.table.setHorizontalHeaderLabels(headers)
        self.table.resizeColumnsToContents()
        for i in range(len(measdef.getElements())):
            self.table.setColumnWidth(i, max(50, 1.5 * self.table.columnWidth(i)))
        self.table.resizeRowsToContents()

    def keyPressEvent(self, event):
        # do not close the whole dialog when pressing Enter in an input box
        if event.key() == Qt.Key_Return:
            return
        return QDialog.keyPressEvent(self, event)

    def toDefs(self):
        return [self._rows]

    def _stopEdit(self):
        i, j, eltype = self._edit
        element = self._rows[i][eltype]
        element.destroyWidget()
        # apply constraints of the widget to other entries
        for k, (othereltype, otherelement) in enumerate(self._rows[i].items()):
            if othereltype == element.eltype:
                continue
            otherelement.otherChanged(element.eltype, element.getValue())
            self.table.item(i, k).setText(otherelement.getDispValue())
        self.table.setCellWidget(i, j, None)
        self.table.item(i, j).setText(element.getDispValue())
        self._edit = None

    def on_buttonBox_accepted(self):
        if self._edit:
            self._stopEdit()

    def on_table_cellActivated(self, i, j):
        if self._edit:
            self._stopEdit()
        element = self._rows[i].values()[j]
        # create edit widget
        widget = element.createWidget(self, self.client)
        # apply constraints to the widget from other entries
        for othereltype, otherelement in self._rows[i].items():
            if othereltype == element.eltype:
                continue
            element.otherChanged(othereltype, otherelement.getValue())
        # show widget in table
        widget.setFocus()
        self.table.setCellWidget(i, j, widget)
        self._edit = (i, j, element.eltype)

    @pyqtSlot()
    def on_addBtn_clicked(self):
        dic = OrderedDict()
        for eltype, cls in self.measdef.getElements():
            value = self._new_elements[eltype].getValue()
            dic[eltype] = cls(eltype, self.client, value)
        self.addRow(dic)

    def addRow(self, dic):
        if self._edit:
            self._stopEdit()
        self._rows.append(dic)
        last = self.table.rowCount()
        self.table.setRowCount(last + 1)
        for i, (eltype, _) in enumerate(self.measdef.getElements()):
            item = QTableWidgetItem(dic[eltype].getDispValue())
            self.table.setItem(last, i, item)
        self.table.resizeRowsToContents()

    @pyqtSlot()
    def on_downBtn_clicked(self):
        if self._edit:
            self._stopEdit()
        ix = self.table.currentRow()
        if ix < 0 or ix == self.table.rowCount() - 1:
            return
        ncols = self.table.columnCount()
        for j in range(ncols):
            item = self.table.takeItem(ix, j)
            self.table.setItem(ix, j, self.table.takeItem(ix + 1, j))
            self.table.setItem(ix + 1, j, item)
        self._rows[ix], self._rows[ix + 1] = self._rows[ix + 1], self._rows[ix]
        self.table.setCurrentCell(ix + 1, self.table.currentColumn())
        self.table.setRangeSelected(
            QTableWidgetSelectionRange(ix + 1, 0, ix + 1, ncols - 1), True)

    @pyqtSlot()
    def on_upBtn_clicked(self):
        if self._edit:
            self._stopEdit()
        ix = self.table.currentRow()
        if ix < 0 or ix == 0:
            return
        ncols = self.table.columnCount()
        for j in range(ncols):
            item = self.table.takeItem(ix, j)
            self.table.setItem(ix, j, self.table.takeItem(ix - 1, j))
            self.table.setItem(ix - 1, j, item)
        self._rows[ix], self._rows[ix - 1] = self._rows[ix - 1], self._rows[ix]
        self.table.setCurrentCell(ix - 1, self.table.currentColumn())
        self.table.setRangeSelected(
            QTableWidgetSelectionRange(ix - 1, 0, ix - 1, ncols - 1), True)

    @pyqtSlot()
    def on_delBtn_clicked(self):
        if self._edit:
            self._stopEdit()
        ix = self.table.currentRow()
        if ix < 0:
            return
        del self._rows[ix]
        self.table.removeRow(ix)

    @pyqtSlot()
    def on_clearBtn_clicked(self):
        if self._edit:
            self._stopEdit()
        del self._rows[:]
        while self.table.rowCount():
            self.table.removeRow(0)


class DevicesWidget(QWidget):
    remove = pyqtSignal(object)

    def __init__(self, parent, client, devs):
        self.client = client
        self.devs = devs
        QWidget.__init__(self, parent)
        loadUi(self, findResource('custom/kws1/lib/gui/devices_one.ui'))

        self.table.setColumnCount(len(devs))
        self.table.setHorizontalHeaderLabels(devs)
        self._edit = None
        self._rows = []

    def keyPressEvent(self, event):
        # do not close the whole dialog when pressing Enter in an input box
        if event.key() == Qt.Key_Return:
            return
        return QDialog.keyPressEvent(self, event)

    def getDef(self):
        if self._edit:
            self._stopEdit()
        return [dict((dev, element) for (dev, element) in zip(self.devs, row))
                for row in self._rows]

    def addRow(self, elements=None):
        if self._edit:
            self._stopEdit()
        last = self.table.rowCount()
        self.table.setRowCount(last + 1)
        if elements is None:
            elements = [Device(dev, self.client) for dev in self.devs]
        for (i, element) in enumerate(elements):
            self.table.setItem(last, i,
                               QTableWidgetItem(element.getDispValue()))
        self._rows.append(elements)
        self.table.resizeRowsToContents()

    def _stopEdit(self):
        i, j, element = self._edit
        element.destroyWidget()
        self.table.setCellWidget(i, j, None)
        self.table.item(i, j).setText(element.getDispValue())
        self._edit = None

    def on_table_cellActivated(self, i, j):
        if self._edit:
            self._stopEdit()
        element = self._rows[i][j]
        widget = element.createWidget(self, self.client)
        widget.setFocus()
        self.table.setCellWidget(i, j, widget)
        self.table.item(i, j).setText('')
        self._edit = (i, j, element)

    @pyqtSlot()
    def on_clearBtn_clicked(self):
        self.remove.emit(self)

    @pyqtSlot()
    def on_addBtn_clicked(self):
        self.addRow()

    @pyqtSlot()
    def on_downBtn_clicked(self):
        if self._edit:
            self._stopEdit()
        ix = self.table.currentRow()
        if ix < 0 or ix == self.table.rowCount() - 1:
            return
        ncols = self.table.columnCount()
        for j in range(ncols):
            item = self.table.takeItem(ix, j)
            self.table.setItem(ix, j, self.table.takeItem(ix + 1, j))
            self.table.setItem(ix + 1, j, item)
        self._rows[ix], self._rows[ix + 1] = self._rows[ix + 1], self._rows[ix]
        self.table.setCurrentCell(ix + 1, self.table.currentColumn())
        self.table.setRangeSelected(
            QTableWidgetSelectionRange(ix + 1, 0, ix + 1, ncols - 1), True)

    @pyqtSlot()
    def on_upBtn_clicked(self):
        if self._edit:
            self._stopEdit()
        ix = self.table.currentRow()
        if ix < 0 or ix == 0:
            return
        ncols = self.table.columnCount()
        for j in range(ncols):
            item = self.table.takeItem(ix, j)
            self.table.setItem(ix, j, self.table.takeItem(ix - 1, j))
            self.table.setItem(ix - 1, j, item)
        self._rows[ix], self._rows[ix - 1] = self._rows[ix - 1], self._rows[ix]
        self.table.setCurrentCell(ix - 1, self.table.currentColumn())
        self.table.setRangeSelected(
            QTableWidgetSelectionRange(ix - 1, 0, ix - 1, ncols - 1), True)

    @pyqtSlot()
    def on_delBtn_clicked(self):
        if self._edit:
            self._stopEdit()
        ix = self.table.currentRow()
        if ix < 0:
            return
        del self._rows[ix]
        self.table.removeRow(ix)


# Devices that should not appear in the list of additional devices to move,
# because they are already covered by the detector/collimation/... dialog.
DEV_BLACKLIST = set((
    'ap_sam',
    'chopper',
    'chopper_params',
    'collimation',
    'coll_guides',
    'det_nosave',
    'det_x',
    'det_y',
    'det_z',
    'detector',
    'flipper',
    'lenses',
    'pol_switch',
    'polarizer',
    'sam_rot',
    'sam_trans_x',
    'sam_trans_y',
    'selector',
    'selector_speed',
    'selector_lambda',
    'shutter',
    'sixfold_shutter',
))


class DevicesDialog(QDialog):

    def __init__(self, parent, measdef, client):
        self.measdef = measdef
        self.client = client
        QDialog.__init__(self, parent)
        loadUi(self, findResource('custom/kws1/lib/gui/devices.ui'))

        self.frame = QFrame(self)
        self.scrollArea.setWidget(self.frame)
        self.frame.setLayout(QVBoxLayout())
        self.frame.layout().setContentsMargins(0, 0, 10, 0)
        self.frame.layout().addStretch()

        devlist = client.getDeviceList('nicos.core.device.Moveable')
        for dev in devlist:
            if dev not in DEV_BLACKLIST:
                QListWidgetItem(dev, self.devList)

        self._widgets = []

        for group in measdef.devices:
            devs = group[0].keys()
            w = self._addWidget(devs)
            for entry in group:
                w.addRow([entry[x] for x in devs])

    def toDefs(self):
        return [w.getDef() for w in self._widgets]

    def _addWidget(self, devs):
        w = DevicesWidget(self.frame, self.client, devs)
        self.frame.layout().insertWidget(self.frame.layout().count()-1, w)
        w.remove.connect(self.on_removeWidget)
        self._widgets.append(w)
        return w

    @pyqtSlot()
    def on_addBtn_clicked(self):
        devs = []
        for item in self.devList.selectedItems():
            devs.append(item.text())
        if not devs:
            return
        self.devList.clearSelection()
        w = self._addWidget(devs)
        w.addRow()

    def on_removeWidget(self, widget):
        self.frame.layout().removeWidget(widget)
        self._widgets.remove(widget)
        widget.deleteLater()


class RtConfigDialog(QDialog):

    DEFAULT_SETTINGS = {
        'channels': 1,
        'interval': 1,
        'intervalunit': 0,  # us
        'progq': 1.0,
        'trigger': 'external',
        'totaltime': 0.,    # s
    }

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        loadUi(self, findResource('custom/kws1/lib/gui/rtconfig.ui'))
        self.progBox.setValidator(DoubleValidator(self))
        self.chanBox.valueChanged.connect(self._update_time)
        self.intervalBox.valueChanged.connect(self._update_time)
        self.intervalUnitBox.currentIndexChanged.connect(self._update_time)
        self.linBtn.toggled.connect(self._update_time)
        self.progBtn.toggled.connect(self._update_time)
        self.progBox.textChanged.connect(self._update_time)

    def _update_time(self):
        self.totalLbl.setText('Total time: %s' %
                              formatDuration(self.getSettings()['totaltime']))

    def setSettings(self, settings):
        self.chanBox.setValue(settings['channels'])
        self.intervalBox.setValue(settings['interval'])
        self.intervalUnitBox.setCurrentIndex(settings['intervalunit'])
        if settings['progq'] == 1.0:
            self.linBtn.setChecked(True)
        else:
            self.progBtn.setChecked(True)
        self.progBox.setText(str(settings['progq']))
        if settings['trigger'] == 'external':
            self.extBtn.setChecked(True)
        else:
            self.immBtn.setChecked(True)
        self._update_time()

    def getSettings(self):
        progq = float(self.progBox.text())
        settings = {
            'channels': self.chanBox.value(),
            'interval': self.intervalBox.value(),
            'intervalunit': self.intervalUnitBox.currentIndex(),
            'progq': 1.0 if self.linBtn.isChecked() else progq,
            'trigger': 'external' if self.extBtn.isChecked() else 'immediate',
        }
        tottime = 0
        interval = settings['interval'] * \
            {0: 1, 1: 1e3, 2: 1e6}[settings['intervalunit']]
        q = settings['progq']
        for i in range(settings['channels']):
            tottime += int(interval * q**i)
        settings['totaltime'] = tottime / 1000000.
        return settings
