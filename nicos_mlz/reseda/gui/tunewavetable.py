#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from pprint import pformat
from datetime import datetime

from nicos.guisupport.qt import pyqtSignal, pyqtSlot, Qt, QEvent, QDateTime, \
    QMenu, QTableWidgetItem, QGraphicsView, QFont, QColor, QGraphicsLineItem, \
    QGraphicsScene, QPen, QBrush, QGraphicsEllipseItem, QPainter, \
    QGraphicsTextItem, QDialog, QTextEdit, QFrame

from nicos.utils import findResource
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.typedvalue import DeviceValueEdit
from nicos.pycompat import iteritems, xrange  # pylint: disable=W0622


class TimelineWidget(QGraphicsView):
    """General widget to display timeline with a list of ordered timepoints.
    A timepoint is selectable via click and the timepointSelected signal
    can be used to react to it."""
    timepointSelected = pyqtSignal(object)  # datetime.datetime object

    # general layout and design parameters
    TIMEPOINT_DIAMETER = 30
    SELECTION_DIAMETER = 40
    TIMEPOINT_SPACING = 50
    TIMELINE_WIDTH = 5
    LABEL_SPACING = 20
    MARGIN_HORIZONTAL = 5
    STRFTIME_FMT = '%H:%M:%S\n%Y-%m-%d'

    def __init__(self, parent=None):
        QGraphicsView.__init__(self, QGraphicsScene(), parent)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setRenderHints(QPainter.Antialiasing
                            | QPainter.SmoothPixmapTransform)

        # margins set to 0 to simplify calculations
        self.setContentsMargins(0, 0, 0, 0)
        self.setViewportMargins(0, 0, 0, 0)

        # full viewport updates required to avoid optical double selections
        # caused by scrolling
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self._time_points = []
        self._time_point_items = {}
        self._selection_item = None

        # start with at least one time point (current time) to be able
        # to reuse size calculation methods for the inital size
        self.setTimePoints([datetime.now()])

    @property
    def time_points(self):
        """Sorted list of all timepoints (sorted new to old)"""
        return self._time_points

    @property
    def selected_time_point(self):
        """Get the selected timeout as datetime object. None if there is no
        selection."""
        if self._selection_item is None:
            return None

        return self._time_point_items[self._selection_item]

    @property
    def previous_time_point(self):
        """Get the timepoint before (older than) the currently selected one as
        datetime object. None if there is no selection"""
        try:
            index = self._time_points.index(self.selected_time_point)
            return self._time_points[index + 1]
        except (ValueError, IndexError):
            return None

    def resizeEvent(self, event):
        """Clear and readd all items on resize. Avoids complex scaling."""
        self.scene().clear()
        self.setTimePoints(self._time_points)

    def setTimePoints(self, time_points):
        """Sets and list of datetime objects as timepoints, sets up all
        necessary graphics items and adjusts sizes."""

        self.scene().clear()
        self._selection_item = None

        # store the timepoints sorted from new to old
        self._time_points = list(reversed(sorted(time_points)))
        self._time_point_items = {}

        # draw the timeline
        self._timeline = self._add_timeline()

        # draw the time points
        self._add_time_points()

        # update the scene size and a slightly larger widget size to avoid
        # superfluous scrolling (and displaying of scroll bars)
        size = self.scene().itemsBoundingRect().size()
        self.setSceneRect(0, 0, size.width(), size.height() - 5)

        if time_points:
            self.setMinimumWidth(size.width() * 1.2)
            self.setMaximumWidth(size.width() * 1.2)

    def mousePressEvent(self, event):
        """Handle mouse press events to support item selection."""
        item = self.itemAt(event.pos())
        if item in self._time_point_items:
            self._select_item(item)

        return QGraphicsView.mousePressEvent(self, event)

    def _select_item(self, item):
        """Select the given item by drawing a colored circle beneath the
        selected item (so it looks like a ring around it.
        Also emits the timepointSelected signal."""

        # The selection_item used to signal the selection of a timepoint
        # is always the same and is only moved.
        if self._selection_item is None:
            self._selection_item = QGraphicsEllipseItem(0, 0,
                                                        self.SELECTION_DIAMETER,
                                                        self.SELECTION_DIAMETER)

            # The used color is a cubical to the time point color
            self._selection_item.setBrush(QBrush(QColor(0x70, 0xbb, 0x00)))
            self._selection_item.setPen(QPen(0))
            self.scene().addItem(self._selection_item)

        # center position of the timepoint circle
        center_x = item.pos().x() + self.TIMEPOINT_DIAMETER / 2
        center_y = item.pos().y() + self.TIMEPOINT_DIAMETER / 2

        # move selection item
        self._selection_item.setPos(center_x - self.SELECTION_DIAMETER / 2,
                                    center_y - self.SELECTION_DIAMETER / 2)

        # store the selection_item like a timepoint item (using the timepoint
        # of the selected item)
        self._time_point_items[self._selection_item] = \
            self._time_point_items[item]

        # emit signal at the end to ensure a valid internal state before
        # anything can react to it
        self.timepointSelected.emit(self._time_point_items[item])

    def _add_timeline(self):
        """Draw the timeline."""

        # height is either the necessary space to display all items or the
        # maximal available display size, so it's looks nicely in larger
        # windows and enables scrolling in smaller ones.
        height = self.TIMEPOINT_DIAMETER * len(self._time_points)
        height += self.TIMEPOINT_SPACING * len(self._time_points)
        height = max(height, self.viewport().height())

        # draw the timeline left aligned with enough space to draw the items
        # and the selection ring.
        x = self.MARGIN_HORIZONTAL + (self.SELECTION_DIAMETER / 2)

        # position the line on the left side of the item
        item = QGraphicsLineItem(0, 0, 0, height)

        # The used color for the timeline is the lightest one of the FRM II
        # colors
        item.setPen(QPen(QBrush(QColor(0xa3, 0xc1, 0xe7)), self.TIMELINE_WIDTH))

        self.scene().addItem(item)

        # move the whole item to the desired timeline position
        item.setPos(x, 0)
        return item

    def _add_time_points(self):
        """Add all time point items."""
        if not self._time_points:
            return

        timeline_pos = self._timeline.pos()
        timeline_size = self._timeline.boundingRect().size()
        height = timeline_size.height()

        # time points are always equally distributed on the timeline
        spacing = height / float(len(self._time_points))

        center_x = timeline_pos.x()

        # add half of the items spacing on the top and bottom of the timeline
        start = timeline_pos.y() - spacing / 2

        for i, entry in enumerate(self._time_points):
            self._add_time_point(center_x, start + spacing * (i + 1), entry)

    def _add_time_point(self, center_x, center_y, time_point):
        """Add a single time point item."""
        x = center_x - (self.TIMEPOINT_DIAMETER / 2)
        y = center_y - (self.TIMEPOINT_DIAMETER / 2)

        # Create the acutal time point item
        time_point_item = QGraphicsEllipseItem(0, 0, self.TIMEPOINT_DIAMETER,
                                               self.TIMEPOINT_DIAMETER)

        # The used color is the strongest one of the FRM II colors.
        time_point_item.setBrush(QBrush(QColor(0x00, 0x71, 0xbb)))
        time_point_item.setPen(QPen(0))

        self.scene().addItem(time_point_item)
        time_point_item.setPos(x, y)

        # place the time point item above the timeline and the selection item
        time_point_item.setZValue(2)

        # Create the label of the time point showing the time in the
        # defined strftime format on the right side of the time point item.
        label = QGraphicsTextItem(time_point.strftime(self.STRFTIME_FMT))
        label.setFont(QFont('Monospace'))
        label_height = label.boundingRect().height()

        # minor height adjustment
        label_y = y - label_height / 6

        self.scene().addItem(label)
        label.setPos(x + self.SELECTION_DIAMETER + self.LABEL_SPACING, label_y)

        # store references to the item and the timepoint in the same dict
        # to be able to use it for forward and reverse lookup
        self._time_point_items[time_point] = time_point_item
        self._time_point_items[time_point_item] = time_point


class PreviewDialog(QDialog):
    """Dialog to preview the history of a specific tunewave table."""
    def __init__(self, measmode, wavelength, header_labels, current_table,
                 client, parent):
        QDialog.__init__(self, parent)
        loadUi(self,
               findResource('nicos_mlz/reseda/gui/tunewavetablepreviewdlg.ui'))

        self._client = client
        self._measmode = measmode
        self._wavelength = float(wavelength)
        self._header_labels = header_labels
        self._current_table = current_table
        self._shown_table = None

        self._history = {}  # {datetime: table}

        self.measmodeLabel.setText(measmode)
        self.wavelengthLabel.setText(wavelength)
        self.timeline = TimelineWidget()
        self.horizontalLayout.insertWidget(0, self.timeline)

        self.tableWidget.setColumnCount(len(self._header_labels))
        self.tableWidget.setHorizontalHeaderLabels(self._header_labels)

        self.fromDateTimeEdit.setDateTime(QDateTime.currentDateTime().addMonths(-1))
        self.toDateTimeEdit.setDateTime(QDateTime.currentDateTime())

        self.fromDateTimeEdit.dateTimeChanged.connect(self.update_timeline)
        self.toDateTimeEdit.dateTimeChanged.connect(self.update_timeline)
        self.timeline.timepointSelected.connect(self.update_table)
        self.diffNoneRadioButton.toggled.connect(self.update_table)
        self.diffCurrentRadioButton.toggled.connect(self.update_table)
        self.diffPreviousRadioButton.toggled.connect(self.update_table)

        self.update_timeline()

    @property
    def table(self):
        """Accesses the currently shown table."""
        return self._shown_table

    @property
    def diff_table(self):
        """Returns the table with should be used to compare against for the
        difference display."""
        if self.diffCurrentRadioButton.isChecked():
            # The current table is the currently active tunewave table (not
            # the currently shown table)
            return self._current_table
        elif self.diffPreviousRadioButton.isChecked():
            # The previous table is the the table of the time point previous
            # to the selected one.
            time_point = self.timeline.previous_time_point
            if time_point is not None:
                return self._history[time_point]

        return None

    def update_timeline(self):
        """Updates what time points shall be shown on the timeline."""
        fromtime = self.fromDateTimeEdit.dateTime().toTime_t()
        totime = self.toDateTimeEdit.dateTime().toTime_t()

        result = self._client.ask('gethistory', 'echotime/tables',
                                  str(fromtime), str(totime))

        # Store the history result in the format {datetime: table}
        self._history = {}  # timestamp : table
        for timestamp, tables in result:
            # store time point only if there was a change in the specific table
            if self._measmode in tables:
                if self._wavelength in tables[self._measmode]:
                    self._history[datetime.fromtimestamp(timestamp)] = \
                        tables[self._measmode][self._wavelength]

        # Update the timeline with the discovered time points
        self.timeline.setTimePoints(list(self._history))

    def update_table(self):
        """Updates the currently show table."""
        if not self.timeline.selected_time_point:
            return

        # caches a reference to the table that shall be shown
        self._shown_table = self._history[self.timeline.selected_time_point]

        # cache the table to diff against
        diff_table = self.diff_table

        # clear the table widget but preserve the header labels
        self.tableWidget.setRowCount(0)

        # prepare the table widget with enough rows for later cell widget sets
        self.tableWidget.setRowCount(len(list(self._shown_table)))

        for i, echotime in enumerate(sorted(self._shown_table)):
            # create dict from readonlydict
            row_data = dict(self._shown_table[echotime])

            # add the separate echotime as row entry
            row_data['echotime'] = echotime

            self._add_row(i, row_data, diff_table)

    def _add_diff(self, cell_widget, diff_value):
        """Add the diff value to the cell content and highlight the cell."""
        diff = ' <span style="color:gray;">%s</span>' % diff_value
        cell_widget.setHtml(cell_widget.toPlainText() + diff)
        cell_widget.setStyleSheet('QTextEdit{border:1px solid orange}')

    def _add_row(self, row, row_data, diff_table):
        """Add a row to the table and add/highlight differences."""
        echotime = row_data['echotime']

        for header, value in iteritems(row_data):
            # Use a QTextEdit to be able to use HTML/CSS inside the content
            # (used for displaying the differences)
            widget = QTextEdit(str(value))

            if diff_table is not None:
                diff_value = ''
                show_diff = False

                if echotime in diff_table:
                    # If the echotime exists on both tables, only show the
                    # differences
                    diff_value = diff_table[echotime].get(header, '')
                    if header != 'echotime' and diff_value != value:
                        show_diff = True
                else:
                    # If the echotime is completely new, highlight the whole
                    # row
                    show_diff = True

                if show_diff:
                    self._add_diff(widget, diff_value)

            widget.setReadOnly(True)

            # Don't show any frame as there is the more fancy table grid
            widget.setFrameStyle(QFrame.NoFrame)
            self.tableWidget.setCellWidget(row,
                                           self._header_labels.index(header),
                                           widget)


class TunewaveTableItem(QTableWidgetItem):
    """Custom table widget item that store its content in the actual type
    (instead of string only) and supports comparisons based on that actual
    value."""
    def __init__(self, value):
        QTableWidgetItem.__init__(self, str(value))
        self.value = value

    def __lt__(self, other):
        return self.value.__lt__(other.value)

    def __gt__(self, other):
        return self.value.__gt__(other.value)


class TunewaveTablePanel(Panel):
    """Panel to access and edit the reseda tunewave tables.
    It requires the ``echotime`` device to be loaded and working."""

    panelName = 'Tunewave table'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, findResource('nicos_mlz/reseda/gui/tunewavetable.ui'))

        # access to the echotime device
        self._dev = None

        self._header_labels = []
        self._available_tables = {}
        self._edit = None
        self._blocked_while_edit = [self.measModeComboBox,
                                    self.wavelengthComboBox,
                                    self.restorePushButton,
                                    self.savePushButton,
                                    self.refreshPushButton,
                                    self.deletePushButton]

        self.tableWidget.installEventFilter(self)

        self.tableWidget.verticalHeader().setContextMenuPolicy(
            Qt.CustomContextMenu)

        self.measModeComboBox.currentIndexChanged.connect(self._fill_table)
        self.measModeComboBox.currentIndexChanged.connect(
            self._update_combo_boxes)
        self.wavelengthComboBox.currentIndexChanged.connect(self._fill_table)
        self.savePushButton.clicked.connect(self._save_current_table)
        self.refreshPushButton.clicked.connect(self._update_available_tables)
        self.tableWidget.verticalHeader()\
            .customContextMenuRequested.connect(
            self.on_tableWidget_customContextMenuRequested)
        self.tableWidget.cellActivated.connect(self._edit_cell)
        self.tableWidget.verticalHeader().sectionClicked.connect(
            self._stop_edit)
        self.tableWidget.horizontalHeader().sectionPressed.connect(
            self._stop_edit)

        client.connected.connect(self.on_client_connected)

    @property
    def measurement_mode(self):
        return self.measModeComboBox.currentText()

    @property
    def wavelength(self):
        return self.wavelengthComboBox.currentText()

    def setOptions(self, options):
        """Supported panel options:

        tabledev: echotime device name
        """
        Panel.setOptions(self, options)

        self._dev = options['tabledev']

    def eventFilter(self, receiver, event):
        """Event filter for the table widget to stop cell editing on enter
        and return keys."""
        if receiver is self.tableWidget and self._edit is not None \
            and event.type() in [QEvent.KeyPress] \
                and event.key() in [Qt.Key_Enter, Qt.Key_Return]:
            self._stop_edit()
            return True
        return Panel.eventFilter(self, receiver, event)

    def on_client_connected(self):
        """Refresh everything on a fresh connection."""
        self._prepare_table()
        self._update_available_tables()

    @pyqtSlot()
    def on_restorePushButton_clicked(self):
        """Restore an old version of the current table via a advances preview
        dialog."""
        dlg = PreviewDialog(self.measurement_mode, self.wavelength,
                            self._header_labels,
                            self._get_current_table_data(), self.client, self)
        if dlg.exec_():
            self._save_current_table(dlg.table)

    @pyqtSlot()
    def on_deletePushButton_clicked(self):
        """Delete current table after an additional confirmation."""
        if self.askQuestion('Really delete tunewave table %s/%s?'
                            % (self.measurement_mode, self.wavelength),
                            True):
            self._delete_current_table()

    def on_tableWidget_customContextMenuRequested(self, point):
        """Show context menu for adding and deleting echotimes (rows)."""
        self._stop_edit()

        menu = QMenu(self)
        add = menu.addAction('Add echo time')
        delete = menu.addAction('Delete echo time')

        row = self.tableWidget.rowAt(point.y())

        # Disable the delete action if there is nothing to delete
        if row == -1:
            delete.setEnabled(False)

        sender = self.sender()
        # The Signal can be sent from the table widget itself or from the
        # vertical header. In case of the table widget, its viewport hast to be
        # used for correct placement of the context mneu
        if hasattr(sender, 'viewport'):
            sender = sender.viewport()

        action = menu.exec_(sender.mapToGlobal(point))

        if action == add:
            self._add_row(row)
        elif action == delete:
            self._delete_row(row)

    def on_tableWidget_currentCellChanged(self):
        """Stop the editting when the user changed the cell."""
        self._stop_edit()

    def _add_row(self, row, row_data=None):
        """Add a new row to the current tunewave table."""

        if row_data is None:
            row_data = {}

        # If no specific position is given, append the row to the end
        if row == -1:
            row = self.tableWidget.rowCount()

        self.tableWidget.insertRow(row)

        # Fill the row with the given data (if any)
        for param, value in iteritems(row_data):
            item = TunewaveTableItem(value)
            self.tableWidget.setItem(row, self._header_labels.index(param),
                                     item)

    def _delete_row(self, index):
        """Remove the whole row from the table widget."""
        self.tableWidget.removeRow(index)

    def _edit_cell(self, row, column):
        """Start editting of the cell by showing a DeviceValueEdit for it
        (using the current cell value if any)."""
        self._stop_edit()

        if self._edit is not None:
            # Edit wasn't stopped.
            return

        # Create the DeviceValueEdit, using the column header as device name
        item = self.tableWidget.item(row, column)
        widget = DeviceValueEdit(self.tableWidget,
                                 dev=self._header_labels[column],
                                 showUnit=False)
        widget.setAutoFillBackground(True)

        # Forward the NicosClient to the DeviceValueEdit
        widget.setClient(self.client)

        # Fill the DeviceValueEdit with the current cell data (if any)
        if item:
            widget.setValue(item.text())

        self.tableWidget.setCellWidget(row, column, widget)

        # Focus the edit widget and select the contents if possible to provide
        # an 'instant typing' look and feel
        widget.setFocus()
        if hasattr(widget._inner, 'selectAll'):
            widget._inner.selectAll()

        for entry in self._blocked_while_edit:
            entry.setEnabled(False)

        # store information about the current edit process
        self._edit = (row, column, widget)

    def _stop_edit(self):
        """Stop the current edit process, hiding the edit widget and storing
        the new value."""
        if self._edit is None:
            return

        row, column, widget = self._edit
        try:
            value = widget.getValue()
        except ValueError as e:
            self.showError('Invalid input: %s' % e)
            widget.setFocus()
            return

        if column == 0:
            # first column is always echotime

            # forbid multiple echotimes with the same value
            same_value_items = self.tableWidget.findItems(str(value),
                                                          Qt.MatchExactly)

            for entry in same_value_items:
                if self.tableWidget.column(entry) == 0 \
                        and entry != self.tableWidget.item(row, column):
                    self.showError('Echotime already existant, please edit the'
                                   ' particular row or choose another echotime'
                                   ' (typo?).')
                    widget.setFocus()
                    return

        # remove the edit widget and the edit process cache
        self.tableWidget.removeCellWidget(row, column)

        # Store the new value from the edit widget in the particular cell item
        self.tableWidget.setItem(row, column,
                                 TunewaveTableItem(value))

        self._adjust_table_sizes()

        for entry in self._blocked_while_edit:
            entry.setEnabled(True)

        self._edit = None

    def _delete_current_table(self):
        """Delete the currently shown/selected table from the server side table
        storage."""
        self._stop_edit()

        self.client.eval('%s.deleteTable("%s", %s)' % (self._dev,
                                                       self.measurement_mode,
                                                       self.wavelength))
        # Update the internal table cache after the change to the server side
        # storage
        self._update_available_tables()

    @pyqtSlot()
    def _save_current_table(self, table=None):
        """Save the currently shown/selected table to the server side table
        storage."""
        self._stop_edit()

        # If no specific table (like on restore) is given, use the current table
        # data
        if table is None:
            table = self._get_current_table_data()

        self.client.eval('%s.setTable("%s", %s,\n %s)' % (self._dev,
                                                          self.measurement_mode,
                                                          self.wavelength,
                                                          pformat(table)))

        # Update the internal table cache after the change to the server side
        # storage
        self._update_available_tables()

    def _prepare_table(self):
        """Queries tuning device names and sets them as table headers."""

        # Add echotime as first table header
        self._header_labels = ['echotime'] + self.client.eval('%s.tunedevs'
                                                              % self._dev)

        # Add the particular device unit to the device name in the column header
        labels = []
        for entry in self._header_labels:
            unit = self.client.getDeviceParam(entry, 'unit')
            if unit:
                entry = '%s (%s)' % (entry, unit)
            labels.append(entry)

        self.tableWidget.setColumnCount(len(labels))
        self.tableWidget.setHorizontalHeaderLabels(labels)

    def _fill_table(self):
        """Request the currently selected table from the server side table
        storage and display it in the table widget."""
        table = self.client.eval('%s.getTable("%s", %s)' % (self._dev,
                                                            self.measurement_mode,
                                                            self.wavelength))

        # Disable table sorting while filling to avoid jumping rows
        self.tableWidget.setSortingEnabled(False)

        # Clear table and preserve the column headers
        self.tableWidget.setRowCount(0)

        row = 0
        for echotime, devices in iteritems(table):
            # Create dict from readonly dict
            cols = dict(devices)

            # Add echotime to row data
            cols['echotime'] = echotime

            self._add_row(row, cols)
            row += 1

        # Reenable table sorting
        self.tableWidget.horizontalHeader().setSortIndicator(0,
                                                             Qt.AscendingOrder)
        self.tableWidget.setSortingEnabled(True)

        self._adjust_table_sizes()

    def _get_row_data(self, row):
        """Get the device values for the given row."""
        result = {}

        for i, name in enumerate(self._header_labels):
            # Use the value in the actual type from the custom table item
            try:
                result[name] = self.tableWidget.item(row, i).value
            except AttributeError:
                # no item
                continue

        return result

    def _get_current_table_data(self):
        """Get the full table data of the current table in the correct storage
        format."""
        result = {}
        for i in xrange(self.tableWidget.rowCount()):
            row = self._get_row_data(i)
            echotime = row['echotime']
            del row['echotime']
            result[echotime] = row
        return result

    def _update_combo_boxes(self):
        """Update the contents of the table selection combo boxes by using the
        internal table cache."""
        cur_wavelength = self.wavelength

        # block signals to avoid multiple queries of different tunewave tables
        self.wavelengthComboBox.blockSignals(True)
        self.wavelengthComboBox.clear()

        # Stringify the contents (and add a default wavelength)
        values = map(str, sorted(self._available_tables.get(
            self.measurement_mode, [0.0])))
        self.wavelengthComboBox.addItems(values)

        # Reenable signals for table selection
        self.wavelengthComboBox.blockSignals(False)

        # restore previously shown tunewave table if possible
        if cur_wavelength:
            index = self.wavelengthComboBox.findText(str(float(cur_wavelength)))
            self.wavelengthComboBox.setCurrentIndex(index if index != -1 else 0)
        self._fill_table()

    def _update_available_tables(self):
        """Update internal table cache."""
        self._available_tables = self.client.eval('%s.availtables' % self._dev)
        self._update_combo_boxes()

    def _adjust_table_sizes(self):
        """Adjusts column and row sizes of the table widget to avoid cuts/wraps
        in values or headers."""
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
