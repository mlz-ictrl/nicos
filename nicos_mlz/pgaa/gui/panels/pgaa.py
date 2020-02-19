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
#   Johannes Schwarz <johannes.schwarz@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI PGAA panel components."""

from __future__ import absolute_import, division, print_function

import re
from collections import OrderedDict
from datetime import datetime
from os import path
from uuid import uuid1

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QT_VER, QAbstractItemView, QGridLayout, \
    QHeaderView, QObject, Qt, QTableWidget, QTableWidgetItem, QWidget, \
    pyqtSignal, pyqtSlot
from nicos.protocols.daemon import STATUS_IDLE, STATUS_IDLEEXC, \
    STATUS_RUNNING, STATUS_STOPPING
from nicos.utils import findResource

from .scripthandler import TemplateScriptHandler
from .widgets import AttCell, BeamCell, CellItem, CondCell, DetectorCell, \
    DevSlider, ElCol, ElColCell, FileNum, Led, MotorValue, NameCommentCell, \
    PosCell, PushSlider, StartCell, StatusCell, VacuumView, ValueCell

my_uipath = path.dirname(__file__)


class BasicScriptHandler(object):

    def __init__(self):
        try:
            with open(path.join(my_uipath, 'basic_script.py'), 'r') as f:
                basic_script = f.read()
        except IOError:
            basic_script = ''
        self.basic_script = basic_script
        self.handler = TemplateScriptHandler(basic_script)

    def extract_data(self, text):
        """Extract templated values from script text.

        Values will be put with their names into a dict an returned.
        """
        return self.handler.extract_data(text) if text else {}


class PGAAPanel(Panel):

    panelName = 'PGAA'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_mlz/pgaa/gui/panels/pgaaposition.ui'))

        self.motorslide = DevSlider(client, 'sc', 1, 16, parent=self)
        self.motorslide.setParent(self.MotorGroup)
        self.motorslide.setOrientation(Qt.Horizontal)
        self.motorslide.setGeometry(10, 60, 221, 22)
        self.motorval = MotorValue(client, self)
        self.motorval.setParent(self.MotorGroup)
        self.motorval.setGeometry(10, 30, 221, 23)
        self.press = VacuumView(client, self)
        self.PressureLayout.addWidget(self.press)

        self.shutterled = Led('shutter', 'open', 'closed', client)
        self.shutterled.resize(51, 31)
        gl = QGridLayout()
        gl.addWidget(self.shutterled, 0, 0)
        self.BeamBox.setLayout(gl)

        self.pushmover = PushSlider(client, 'push', parent=self)
        self.pushmover.setParent(self.MotorGroup)
        self.pushmover.setOrientation(Qt.Vertical)
        self.pushmover.setGeometry(240, 25, 22, 51)

        self.ellcol = ElCol(client)
        gl = QGridLayout()
        self.ellcol.resize(51, 32)
        gl.addWidget(self.ellcol, 0, 0)
        self.EllColGroup.setLayout(gl)

        self.attenuatorLed1 = Led('att1', 'in', 'out', client,
                                  colorActive='blue', colorInactive='yellow')
        self.AttLayout.addWidget(self.attenuatorLed1)
        self.attenuatorLed2 = Led('att2', 'in', 'out', client,
                                  colorActive='blue', colorInactive='yellow')
        self.AttLayout.addWidget(self.attenuatorLed2)
        self.attenuatorLed3 = Led('att3', 'in', 'out', client,
                                  colorActive='blue', colorInactive='yellow')
        self.AttLayout.addWidget(self.attenuatorLed3)

        self.filenum = FileNum(client)
        self.filenum.setMaximumWidth(70)
        self.CountLayout.addWidget(self.filenum)

        self.active_table = TableWidget(
            QueueSource(client, self, startwidg=self.startQ),
            QueueSource.column_order, self)
        self.active_table.setSelectionMode(
            QAbstractItemView.SingleSelection)
        self.active_table.handle_drop = self.active_table.source.insert_new
        self.active_table.rearrange = self.active_table.source.rearrange
        self.active_table.keypress = self.active_table.source.keypress
        self.active_table.horizontalHeader().hide()
        self.queueLayout.addWidget(self.active_table)

        self.log_table = TableWidget(LogSource(client, self), Log.column_order,
                                     self)
        self.log_table.setAcceptDrops(False)
        self.log_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.logLayout.addWidget(self.log_table)

        self.pattern_table = TableWidget(Template(client, self),
                                         Row.column_order, self)
        self.pattern_table.setAcceptDrops(False)
        self.pattern_table.keypress = self.pattern_table.source.keypress
        self.templateLayout.addWidget(self.pattern_table)

        self.tracker = ProgressTracker(client, self, self.Name, self.Comment,
                                       self.finish, self.suffixView,
                                       self.stopBy, self.atAfter)

        self.setAcceptDrops(True)

        if client.isconnected:
            self.on_client_connected()
        self.queue_data = None
        client.status.connect(self.on_status)

    def on_status(self, state):
        running = state[0] in [STATUS_RUNNING, STATUS_STOPPING]
        for w in (self.shutterled, self.ellcol, self.attenuatorLed1,
                  self.attenuatorLed2, self.attenuatorLed3, self.pushmover,
                  self.motorslide):
            w.setDisabled(running)


class TableWidget(QTableWidget):

    def __init__(self, source, column_order, parent=None):
        QTableWidget.__init__(self, parent)

        if parent:
            self.log = parent.parent().log
        self.setShowGrid(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        # self.setDragDropOverwriteMode(True)
        # self.setDropIndicatorShown(True)
        self.verticalHeader().hide()
        hdr = self.horizontalHeader()
        if QT_VER == 4:
            hdr.setResizeMode(QHeaderView.Interactive)
        else:
            hdr.setSectionResizeMode(QHeaderView.Interactive)
        # self.setDropIndicatorShown(True)

        self.source = source

        self.hidden_row = None
        self.empty_row = None
        self.state = uuid1()
        self.handle_drop = None
        self.rearrange = None
        self.keypress = None

        self.setColumnHeaders(column_order)
        self.show()

        self.source.set_table(self)
        if hasattr(source, 'sequence') and source.sequence:
            self._refresh()

    def setColumnHeaders(self, column_headers):
        self.setColumnCount(len(column_headers))
        for i, text in enumerate(column_headers):
            self.setHorizontalHeaderItem(i, QTableWidgetItem(text))

    def dragEnterEvent(self, e):
        if e.source() is self:
            if e.mimeData().hasText():
                # drag has been moved out of widget and entering again
                # if e.mimeData().text() == str(self.state):
                #     return
                # else:
                #     return
                pass
            else:
                # dragging row of queued measurement.
                # this row shouldn't be the first one since its most likely
                # a paused measurement which can't be rearranged.
                # TODO: implement in data model
                row_at_pos = self.rowAt(e.pos().y())
                if row_at_pos >= 0:
                    e.mimeData().setText(str(self.state))
                    self.setRowHidden(row_at_pos, True)
                    self.hidden_row = row_at_pos
                else:
                    e.mimeData().setText('fail')
        e.accept()

    def dragMoveEvent(self, e):
        if e.source() is self:
            # checks if  any of the queued data has been changed
            # since this drag started
            if not e.mimeData().text() == str(self.state):
                self.log.info('not same state')
                self.restore()
                return
        row_no = self.rowAt(e.pos().y())

        if self.empty_row is not None and self.empty_row != row_no:
            self.removeRow(self.empty_row)
            self.empty_row = None

        if row_no >= 0 and row_no != self.empty_row:
            self.insertRow(row_no)
            self.empty_row = row_no
        e.accept()

    def dropEvent(self, e):
        row_at = self.empty_row if self.empty_row is not None \
            else self.rowAt(e.pos().y())
        if row_at >= self.rowCount() - 1:
            row_at = -1
        source = self.hidden_row
        if self.hidden_row is not None and self.hidden_row < row_at:
            row_at -= 1
        self.restore()
        if e.source() is not self:
            assert self.hidden_row is None
            self.handle_drop(row_at, e.source())
            return
        elif e.mimeData().text() != str(self.state):
            return
        if row_at == -1:
            row_at = self.rowCount() - 1
        if self.rearrange is not None:
            self.rearrange(source, row_at)

    def exchange(self, old_ind, new_ind, item):
        self.next_state()
        self.removeRow(old_ind)
        item.re_create()
        self.insertRow(new_ind)
        self._putInRow(new_ind, item)

    def append(self, item, index=None):
        self.next_state()
        if isinstance(item, Row):
            rowCount = self.rowCount()
            self.insertRow(rowCount if index is None else index)
            self._putInRow(rowCount if index is None else index, item)
        self.horizontalHeader().setStretchLastSection(True)

    def _refresh(self):
        """Remove all rows and refresh with dev data.

        Target is index for row which should be
        """
        self.next_state()
        self.setRowCount(0)  # clearing list

        for row in self.source.sequence:
            r = self.rowCount()
            self.insertRow(r)
            row.re_create()
            self._putInRow(r, row)

        self.setDragEnabled(True)

    def _putInRow(self, rIndex, Item):
        for i, c in enumerate(Item):
            self.setCellWidget(rIndex, i, c)
        self.resizeColumnsToContents()

    def restore(self):
        if self.empty_row is not None:
            self.removeRow(self.empty_row)
            self.empty_row = None
        if self.hidden_row is not None:
            assert self.isRowHidden(self.hidden_row)
            self.showRow(self.hidden_row)
            self.hidden_row = None

    def keyPressEvent(self, e):
        if self.keypress is not None:
            self.keypress(e)
        else:
            QTableWidget.keyPressEvent(self, e)

    def remove(self, ind):
        self.next_state()
        self.removeRow(ind)

    def next_state(self):
        self.restore()
        self.state = uuid1()


class Row(QWidget):
    par2cell = OrderedDict([
        ('Pos', PosCell),
        ('Name', NameCommentCell),
        ('Comment', NameCommentCell),
        ('Suffix', NameCommentCell),
        ('Attenuator', AttCell),
        ('ElCol', ElColCell),
        ('Beam', BeamCell),
        ('start', StartCell),
        ('stop by', CondCell),
        ('at/after', ValueCell),
        ('Detectors', DetectorCell),
        # ('State': StatusCell),
        # ('started': StartCell),
        # ('stopped': StartCell),
    ])
    column_order = list(par2cell.keys())

    def __init__(self, parent=None, data=None):
        QWidget.__init__(self, parent=parent)
        self.data = data
        self.widgets = self._create_elements(**self.data)

    def _create_elements(self, **kwargs):
        """Create GUI elements."""
        items = []
        for value in self.par2cell:
            if value not in kwargs:
                kwargs[value] = None
            if value not in self.par2cell or self.par2cell[value] is CellItem:
                w = CellItem(self, self, kwargs[value])
            else:
                w = self.par2cell[value](self, parent=self,
                                         state=kwargs[value])
            items.append(w)
            w.setObjectName(value)
        return items

    def re_create(self):
        for widget in self.widgets:
            del widget
        self.widgets = self._create_elements(**self.data)

    def __getitem__(self, index):
        # returns widget
        if index < len(self.widgets) and index >= 0:
            return self.widgets[index]
        raise IndexError

    # def __len__(self):
    #     return len(self.widgets)

    @pyqtSlot('QWidget')
    def cellChanged(self, item):
        pass


class Measurement(BasicScriptHandler, Row):
    """Class containing GUI widgets and controlling their state."""

    suffix_re = re.compile(r'(?P<att>\d*)(?P<elcol>[CE])(?P<beam>O?)'
                           '(?P<vacuum>V?)(?P<suffix>.*)')

    def __init__(self, parent=None, init_script=None):
        BasicScriptHandler.__init__(self)
        # Data dict with key for every column and corresponding data
        self.data = {key.replace('/', '_').replace(' ', '_'): None
                     for key in self.column_order}
        self.data.update(
            {key.replace('/', '_').replace(' ', '_'):
                Row.par2cell[key].standard_value for key in Row.par2cell})
        if isinstance(init_script, dict):
            # print('init script is a dict', init_script)
            self.data.update(init_script)
            self.data.update({'Comment': init_script.get('info', '')})
            tmp = self.data['Filename'].split('_')
            self.data.update({'Name': tmp[1].split('-')[1],
                              'Suffix': self._extract_suffix(tmp[-1])})
        else:
            data = self.extract_data(init_script)
            self.data.update(data)
        # TODO: place stop cond cells in one column
        self.stop_cond_cells = {}
        Row.__init__(self, parent=parent, data=self.data)
        self._make_connections()

    def _extract_suffix(self, txt):
        return self.suffix_re.search('COVX').group('suffix')

    def _make_connections(self):
        condCell = None
        atAfterCell = None
        for w in self.widgets:
            if isinstance(w, CondCell):
                condCell = w
            elif isinstance(w, ValueCell):
                atAfterCell = w
        if condCell and atAfterCell:
            condCell.condChanged.connect(atAfterCell.condCellChanged)
        for w in self.widgets:
            w.cellChanged.connect(self.cellChanged)

    @pyqtSlot('QWidget')
    def cellChanged(self, item):
        """Call back for 'cellChanged' signal."""
        Row.cellChanged(self, item)
        info = item.objectName()
        if info == 'stop by':
            for it in self.widgets:
                if it.objectName() == 'at/after':
                    self.data['at_after'] = it.value(item.value())
            self.data['stop_by'] = item.value()
        else:
            if info == 'at/after':
                info = 'at_after'
            self.data[info] = item.value()

    def get_script(self):
        script = self.basic_script
        for key in self.data:
            script = script.replace(
                '__%s__' % key.replace('/', '_').replace(' ', '_'),
                '%s' % self.data[key])
        return script

    def re_create(self):
        for widget in self.widgets:
            widget.cellChanged.disconnect(self.cellChanged)
            del widget
        self.widgets = self._create_elements(**self.data)
        self._make_connections()

    def is_enabled(self):
        for widget in self.widgets:
            if not widget.is_enabled():
                return False
        return True

    def set_enabled(self, enabled):
        for widget in self.widgets:
            widget.set_enabled(enabled)

    def set_doubleclick(self):
        for widget in self.widgets:
            widget.doubleclick = self.handle_doubleclick

    def handle_doubleclick(self):
        for widget in self.widgets:
            widget.set_enabled(True)


class QueuedMeasurement(Measurement):
    """Control widget state by retrieving daemon update events."""

    disable = False  # Flag to disable measurement entries

    def __init__(self, client, request, parent=None):
        reqname = 'reqid' if 'reqid' in request else 'reqno'
        self.reqid = request[reqname]
        script_text = request['script']
        self._client = client
        Measurement.__init__(self, parent=parent, init_script=script_text)
        atAfterCell = self.widgets[self.column_order.index('at/after')]
        condCell = self.widgets[self.column_order.index('stop by')]
        condCell.setValue(self.data['stop_by'])
        atAfterCell.condCellChanged(self.data['stop_by'])
        atAfterCell.setValue(self.data['at_after'])
        self._client.updated.connect(self.on_update)
        if self.disable:
            for w in self.widgets:
                w.disable()

    @pyqtSlot('QWidget')
    def cellChanged(self, item):
        """Item requesting update(nextstate) calls this method."""
        Measurement.cellChanged(self, item)
        if self.disable:
            item.disable()
        newScript = self.get_script()
        # TODO: sometimes is status is None!
        status = self._client.ask('getstatus')
        if status['script'].startswith('# PGAA'):  # PGAA script runs
            self._client.tell('update', newScript, 'PGAAPanel')
        else:
            for request in status['requests']:
                if request['reqid'] == self.reqid:
                    self._client.tell('update', newScript, 'PGAAPanel',
                                      self.reqid)

    def on_update(self, newreq):
        """If new script differs from old one, the widgets will be updated."""
        reqname = 'reqid' if 'reqid' in newreq else 'reqno'
        if not newreq[reqname] == self.reqid:
            return
        new_data = self.extract_data(newreq['script'])
        self.data.update(new_data)
        for key in new_data:
            k = key
            if k == 'at_after':
                k = 'at/after'
            elif k == 'stop_by':
                k = 'stop by'
            if '__%s__' % key in self.basic_script and \
               k in self.column_order:
                index = self.column_order.index(k)
                self.widgets[index].setValue(new_data[key])


class Log(Row):
    par2cell = OrderedDict([
        ('Filename', StatusCell),
        ('Attenuator', StatusCell),
        ('ElCol', StatusCell),
        ('Beam', StatusCell),
        ('started', StatusCell),
        ('stop by', StatusCell),
        ('at/after', StatusCell),
        ('stopped', StatusCell),
        ('Detectors', StatusCell),
        ('Pressure', StatusCell),
        # ('Pos': StatusCell),
        # ('Code': StatusCell),
        # ('Comment': StatusCell),
    ])
    column_order = list(par2cell.keys())

    def __init__(self, data, controller, parent=None):
        self.stop_cond_cells = {}
        if 'started' in data:
            data['started'] = datetime.fromtimestamp(
                data['started']).strftime('%Y-%m-%d %H:%M:%S')
        if 'stopped' in data:
            data['stopped'] = datetime.fromtimestamp(
                data['stopped']).strftime('%Y-%m-%d %H:%M:%S')
        Row.__init__(self, parent, data)
        for widget in self.widgets:
            widget.setMinimumWidth(90)
            widget.setDisabled(True)


class QueueSource(QObject):
    column_order = Row.column_order

    queuereq = pyqtSignal(QWidget)

    def __init__(self, client, parent=None, startwidg=None, removewidg=None):
        QObject.__init__(self, parent)
        # list containing measurement objects in same order as queued scripts
        # in daemon
        self.sequence = []
        # executed script reqids that should be paused
        self._break_reqs = []
        self._breakreqid = None
        self._client = client
        self._view = None
        # client.sequence.connect(self.on_newsequence)
        client.connected.connect(self.on_init_data)
        client.request.connect(self.on_new_request)
        client.blocked.connect(self.on_blocked)
        client.processing.connect(self.on_processing)
        client.rearranged.connect(self.rearranged)
        self.queuereq.connect(self.on_queuereq)
        startwidg.clicked.connect(self.start)

        if self._client.isconnected:
            self.on_init_data()

    def rearranged(self, ids):
        self.on_init_data()

    def start(self):
        if self._client.tell('continue'):
            if self._breakreqid is not None:
                self._breakreqid = None

    def on_queuereq(self, source):
        # Return pressed on (not enabled) Template should append the script to
        # the queue, increase the pos num on the template by 1 (unless its at
        # 16) and put the focus back on the templates NameCell.
        self.insert_new(-1, source)
        source.setFocus()
        source.selectRow(0)
        namecellno = Row.column_order.index('Name')
        source.source.template.set_enabled(True)
        source.source.template.widgets[namecellno].widgets[0].setFocus()
        poscellno = Row.column_order.index('Pos')
        pos = int(source.source.template.data['Pos']) + 1
        if pos <= 16:
            source.source.template.get_update(
                source.source.template.widgets[poscellno], pos)

    def delete(self, index):
        scriptID = self.sequence[index].reqid
        self._client.tell('unqueue', scriptID)

    def on_newsequence(self, requests):
        """Call back when script orderd changed or scripts are updated."""
        # goal : when 2 items exchanged. exchange func from active table should
        # only be executed once

        def local_ids():
            return [item.reqid for item in self.sequence]

        test = [item.split('-', 1)[0] for item in local_ids()]
        test2 = [item.split('-', 1)[0] for item in requests]
        self.parent().log.fatal('local_ids:%s', ','.join(test))
        self.parent().log.fatal('new_reqs: %s', ','.join(test2))

        for new_ind, request in enumerate(requests):
            # if new_ind >= 1:
            #    assert requests[new_ind-1] == self.sequence[new_ind-1].reqid \
            #       == local_ids()[new_ind-1]

            if not request == local_ids()[new_ind]:
                if local_ids()[new_ind + 1] == request and \
                   requests[new_ind + 1] == local_ids()[new_ind]:
                    index = new_ind
                    next_ind = new_ind + 1
                elif request in local_ids()[new_ind + 2:]:
                    # moved from upper to lower
                    index = local_ids().index(request)
                    next_ind = new_ind
                elif local_ids()[new_ind] in requests[new_ind + 2:]:
                    # moved from lower to upper
                    index = new_ind
                    next_ind = requests.index(local_ids()[new_ind])
                item = self.sequence.pop(index)
                self.sequence.insert(next_ind, item)
                self.viewer.exchange(index, next_ind, item)

    def append_measurement(self, item):
        self.sequence.append(item)
        self.viewer.append(item)

    def on_init_data(self):
        """Collect data from daemon, and init GUI table.

        Checks if queued scripts are PGAAPanel scripts and just append these
        to the internal GUI queue.
        """
        self.sequence = []
        self.viewer._refresh()
        init_Data = self._client.ask('getstatus')

        for request in init_Data['requests']:
            reqname = request.get('name')
            # Checks if queued Scripts are PGAA Scripts
            if reqname and reqname.startswith('PGAAPanel'):
                self.append_measurement(
                    QueuedMeasurement(self._client, request, self.parent()))

    def on_new_request(self, req):
        # check if it's a PGAA script
        reqname = req.get('name')
        if reqname and reqname.startswith('PGAAPanel'):
            reqidname = 'reqid' if 'reqid' in req else 'reqno'
            if req[reqidname] not in [item.reqid for item in self.sequence]:
                self.append_measurement(
                    QueuedMeasurement(self._client, req, self.parent()))

    def queue_script(self, script_data=''):
        # script execution should pause until user wants to start it when queue
        # is empty
        if not self.sequence and \
           not self._break_reqs and \
           self._breakreqid is None:
            self._break_reqs.append(self._client.run('sleep(1)'))
        return self._client.ask('queue', 'PGAAPanel', script_data)

    def rearrange(self, old_ind, new_ind):
        # transmits newly ordered script ids to daemon

        order = [item.reqid for item in self.sequence]
        item = order.pop(old_ind)
        order.insert(new_ind, item)
        if self._break_reqs:
            order.insert(0, self._break_reqs[0])
        if self._client.tell('rearrange', order):
            self.sequence.insert(new_ind, self.sequence.pop(old_ind))
            self.viewer.exchange(old_ind, new_ind, self.sequence[new_ind])
            self.viewer.selectRow(new_ind)

    def on_blocked(self, reqids):
        """Remove measurements with corresponding script-reqid from table."""
        def delete_measurement(reqid):
            # does nothing when script-ID is not in local queue
            for i, item in enumerate(self.sequence):
                if item.reqid == reqid:
                    self.sequence.remove(item)
                    self.viewer.remove(i)
            for item in self._break_reqs:
                if reqid == item:
                    self._break_reqs.remove(item)
        for reqid in reqids:
            delete_measurement(reqid)

    def on_processing(self, processing_req):
        """Call back for daemons 'processing' event."""
        reqname = 'reqid' if 'reqid' in processing_req else 'reqno'
        reqid = processing_req[reqname]

        if reqid in self._break_reqs:
            # script should be paused:
            if self._client.tell('break', 2):
                self._breakreqid = reqid
                self._break_reqs.remove(reqid)
        if processing_req is not None and \
           processing_req['name'] is not None and \
           processing_req['name'].startswith('PGAAPanel'):
            if reqid == self.sequence[0].reqid:
                self.on_blocked([reqid])

    def insert_new(self, index, source):
        if not isinstance(source, TableWidget):
            return
        if isinstance(source.source, Template):
            script_data = source.source.template.get_script()
        elif isinstance(source.source, LogSource):
            logind = source.selectedIndexes()[0].row()
            script_data = Measurement(
                init_script=source.source.sequence[logind].data).get_script()
        else:
            return

        reqid = self.queue_script(script_data)
        if reqid is not None:
            request = {'reqno': reqid, 'reqid': reqid, 'script': script_data}
            new_measurement = QueuedMeasurement(self._client, request,
                                                self.parent())
            self.append_measurement(new_measurement)
            if len(self.sequence) == 1:
                assert self.viewer.rowCount() == 1
            elif not index == -1:
                assert len(self.sequence) == self.viewer.rowCount()
                old_ind = len(self.sequence) - 1
                if not (old_ind == index):
                    self.rearrange(old_ind, index)
                    self.viewer.selectRow(index)
            else:
                self.viewer.selectRow(self.viewer.rowCount() - 1)
            self.viewer.setFocus()

    def keypress(self, e):
        if e.key() == Qt.Key_Delete:
            ind = self.viewer.selectedIndexes()[0].row()
            self.delete(ind)
        else:
            QTableWidget.keyPressEvent(self.viewer, e)

    def set_table(self, table):
        self.viewer = table


class LogSource(QObject):

    def __init__(self, client, parent=None):
        QObject.__init__(self, parent)
        self.sequence = []
        self._client = client
        self.viewer = None
        client.dataset.connect(self.on_new_dataset)
        client.connected.connect(self.init_history)

        if self._client.isconnected:
            self.init_history()

    def on_new_dataset(self, dataset):
        prev = None
        if hasattr(dataset, 'scaninfo'):
            if isinstance(dataset.scaninfo, dict):
                prev = Log(dataset.scaninfo, self, self.viewer)
        else:
            info = dataset.preset.copy()
            info['started'] = dataset.started
            info['stopped'] = dataset.finished
            info['Detectors'] = '[%s]' % ','.join(
                [d for d in dataset.detectors])
            info['Pressure'] = '%.3f mbar' % dataset.metainfo[
                'chamber_pressure', 'value'][0]
            info['Filename'] = info.pop('FILENAME')
            for cond in ['TrueTime', 'LiveTime', 'ClockTime', 'cond']:
                if cond in dataset.preset:
                    info['stop by'] = cond
                    info['at/after'] = dataset.preset[cond]
                    break
            info['Beam'] = dataset.metainfo[dataset.detectors[0],
                                            'enablevalues'][0][0]
            info['Attenuator'] = dataset.metainfo['att', 'value'][0]
            info['ElCol'] = dataset.metainfo['ellcol', 'value'][0]
            prev = Log(info, self, self.viewer)
        if prev:
            self.sequence.insert(0, prev)
            if len(self.sequence) >= 16:
                self.sequence.pop()
                self.viewer.remove(15)
            self.viewer.append(prev, 0)

    def init_history(self):
        datasets = self._client.ask('getdataset', '*')
        if datasets is not None:
            if self.viewer is not None and self.viewer.rowCount() > 0:
                for _i in range(self.viewer.rowCount()):
                    self.viewer.remove(0)
            for item in datasets:
                self.on_new_dataset(item)

    def set_table(self, table):
        self.viewer = table


class Template(QObject):

    def __init__(self, client, parent=None, d60=None, dLEGe=None,
                 filecountedit=None, filenameedit=None):
        QObject.__init__(self, parent)
        self._client = client
        self.template = None
        self.viewer = None
    # def set_template(self):
    #     self.viewer = TableWidget(parent=self.parent(),
    #                                      column_order=Row.column_order)
    #     self.viewer.source = self
    #     self.viewer.append(self.template)
    #     self.viewer.setAcceptDrops(False)
    #     self.viewer.keypress = self.keypress
    #     return self.template_view

    def set_table(self, table):
        self.viewer = table
        self.template = Measurement(self.viewer)
        self.viewer.append(self.template)
        self.template.set_doubleclick()

    def keypress(self, e):
        if e.key() == Qt.Key_Return:
            if self.template.is_enabled():
                # self.template.set_enabled(False)
                self.viewer.setFocus()
                e.accept()
                return
            # TODO: check what was the idea and how to implement it now
            # self._client.queuereq.emit(self.viewer)


class ProgressTracker(BasicScriptHandler, QObject):

    def __init__(self, client, parent, nameview, commentview,
                 finish, suffixview, stop_by, at_after):
        QObject.__init__(self, parent)
        BasicScriptHandler.__init__(self)

        self._client = client
        self.nameview = nameview
        self.commentview = commentview
        self.suffixview = suffixview
        self.stopby = stop_by
        self.atafter = at_after
        self.finish = finish
        if self._client.isconnected:
            self.on_connected()

        self._client.connected.connect(self.on_connected)
        self._client.processing.connect(self.on_processing)
        self._client.status.connect(self.on_status)
        self.finish.clicked.connect(self.on_finish)

    def on_finish(self):
        self._client.tell('finish')

    def on_status(self, statusline):
        status, line = statusline
        if status in (STATUS_IDLE, STATUS_IDLEEXC):
            if (self.basic_script.count('\n') + 1) == line or \
               status == STATUS_IDLEEXC:
                self.clear_widgets()

    def on_connected(self):
        script = self._client.ask('getstatus').get('script', '')
        if script.startswith('# PGAA'):
            self.script2widgets(script)
        else:
            self.clear_widgets()

    def on_processing(self, scriptdata):
        scriptname = scriptdata.get('name')
        if scriptname and scriptname.startswith('PGAAPanel'):
            self.script2widgets(scriptdata.get('script'))
        else:
            self.clear_widgets()

    def clear_widgets(self):
        self.nameview.setText('')
        self.commentview.setText('')
        self.suffixview.setText('')
        self.stopby.setText('')
        self.atafter.setText('')

    def script2widgets(self, script):
        data = self.extract_data(script)
        self.nameview.setText(data.get('Name', ''))
        self.commentview.setText(data.get('Comment', ''))
        self.suffixview.setText(data.get('Suffix', ''))
        self.stopby.setText(data['stop_by'])
        self.atafter.setText(str(data['at_after']))
