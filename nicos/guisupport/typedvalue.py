#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""Widgets for entering values of different NICOS parameter/value types.

The supported types are defined in `nicos.core.params`.
"""

from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QLineEdit, QDoubleValidator, QIntValidator, \
    QCheckBox, QWidget, QComboBox, QHBoxLayout, QVBoxLayout, QLabel, \
    QPushButton, QSpinBox, QScrollArea, QFrame, QSizePolicy, QIcon

from nicos.core import params, anytype
from nicos.protocols.cache import cache_dump, cache_load
from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.pycompat import iteritems


class DeviceValueEdit(NicosWidget, QWidget):

    designer_description = 'Editor for a device value with the right kind ' \
        'of widget'

    def __init__(self, parent, designMode=False, **kwds):
        self._inner = None
        QWidget.__init__(self, parent, **kwds)
        NicosWidget.__init__(self)
        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        if designMode:
            self._layout.insertWidget(0, QLabel('(Value Editor)', self))

    def setFocus(self):
        if self._inner is not None:
            self._inner.setFocus()
        else:
            QWidget.setFocus(self)

    properties = {
        'dev':         PropDef(str, ''),
        'useButtons':  PropDef(bool, False,
                               'Use buttons for values with few choices?'),
        'updateValue': PropDef(bool, False,
                               'Update the editor when the device value changes?'),
    }

    def propertyUpdated(self, pname, value):
        if pname == 'dev':
            self._reinit()
        NicosWidget.propertyUpdated(self, pname, value)

    def setClient(self, client):
        NicosWidget.setClient(self, client)
        self._reinit()

    def on_client_connected(self):
        self._reinit()

    def registerKeys(self):
        if self.props['updateValue']:
            self.registerDevice(self.props['dev'])

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        self._reinit(value)

    def on_devMetaChange(self, dev, fmtstr, unit, fixed):
        self._reinit()

    def _reinit(self, curvalue=None):
        if not self._client or not self._client.connected:
            return
        devname = str(self.props['dev'])
        if devname:
            unit = self._client.getDeviceParam(devname, 'unit')
            fmtstr = self._client.getDeviceParam(devname, 'fmtstr')
            valuetype = self._client.getDeviceValuetype(devname)
            if curvalue is None:
                curvalue = self._client.getDeviceValue(devname)
            if curvalue is None:
                curvalue = valuetype()
        else:
            valuetype = str
            curvalue = ''
            fmtstr = '%s'
            unit = ''
        self._inner = create(self, valuetype, curvalue, fmtstr, unit,
                             allow_buttons=self.props['useButtons'],
                             client=self._client)
        last = self._layout.takeAt(0)
        if last:
            last.widget().deleteLater()
        self._layout.insertWidget(0, self._inner)
        self.connect(self._inner, SIGNAL('dataChanged'), self._changed)
        self.connect(self._inner, SIGNAL('valueChosen'), self._chosen)

    def _changed(self):
        self.emit(SIGNAL('dataChanged'))

    def _chosen(self, value):
        self.emit(SIGNAL('valueChosen'), value)

    def getValue(self):
        if self._inner:
            return self._inner.getValue()

    def setValue(self, value):
        self._reinit(value)


class DeviceParamEdit(DeviceValueEdit):

    designer_description = 'Editor for a device parameter with the right ' \
        'kind of widget'

    properties = {
        'param':       PropDef(str, ''),
    }

    def propertyUpdated(self, pname, value):
        if pname in ('dev', 'param'):
            self._reinit()
        NicosWidget.propertyUpdated(self, pname, value)

    def registerKeys(self):
        self.registerKey(self.props['dev'] + '.' + self.props['param'])

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        if self.props['updateValue']:
            self._reinit(value)

    def _reinit(self, curvalue=None):
        if not self._client:
            return
        devname = str(self.props['dev'])
        parname = str(self.props['param'])
        if devname and parname:
            pvals = self._client.getDeviceParams(devname)
            pinfo = self._client.getDeviceParamInfo(devname) or {}
            mainunit = pvals.get('unit', 'main')
            if parname not in pinfo:
                punit = ''
                valuetype = str
            else:
                punit = (pinfo[parname]['unit'] or '').replace('main', mainunit)
                valuetype = pinfo[parname]['type']
            if curvalue is None:
                curvalue = pvals.get(parname)
            if curvalue is None:
                curvalue = valuetype()
        else:
            valuetype = str
            curvalue = ''
            punit = ''
        self._inner = create(self, valuetype, curvalue, unit=punit,
                             client=self._client)
        last = self._layout.takeAt(0)
        if last:
            last.widget().deleteLater()
        self._layout.insertWidget(0, self._inner)
        self.connect(self._inner, SIGNAL('dataChanged'), self._changed)


def create(parent, typ, curvalue, fmtstr='', unit='',
           allow_buttons=False, client=None):
    # make sure the type is correct
    try:
        curvalue = typ(curvalue)
    except ValueError:
        curvalue = typ()
    if unit:
        inner = create(parent, typ, curvalue, fmtstr, unit='', client=client)
        return AnnotatedWidget(parent, inner, unit)
    if isinstance(typ, params.oneof):
        if allow_buttons and len(typ.vals) <= 3:
            return ButtonWidget(parent, typ.vals)
        return ComboWidget(parent, typ.vals, curvalue)
    elif isinstance(typ, params.oneofdict):
        if allow_buttons and len(typ.vals) <= 3:
            return ButtonWidget(parent, typ.vals.values())
        return ComboWidget(parent, typ.vals.values(), curvalue)
    elif isinstance(typ, params.none_or):
        return CheckWidget(parent, typ.conv, curvalue, client)
    elif isinstance(typ, params.tupleof):
        return MultiWidget(parent, typ.types, curvalue, client)
    elif typ == params.limits:
        return LimitsWidget(parent, curvalue, client)
    elif isinstance(typ, params.floatrange):
        edw = EditWidget(parent, float, curvalue, fmtstr or '%.4g',
                         minmax=(typ.fr, typ.to))
        annotation = '(range: %.5g to %.5g)' % (typ.fr, typ.to) \
            if typ.to is not None else '(must be >= %.5g)' % typ.fr
        return AnnotatedWidget(parent, edw, annotation)
    elif isinstance(typ, params.intrange):
        edw = SpinBoxWidget(parent, curvalue, (typ.fr, typ.to),
                            fmtstr=fmtstr or '%.4g')
        return AnnotatedWidget(parent, edw, '(range: %d to %d)' %
                               (typ.fr, typ.to))
    elif typ in (int, float, str, params.string):
        return EditWidget(parent, typ, curvalue, fmtstr or '%.4g')
    elif typ == bool:
        return ComboWidget(parent, [True, False], curvalue)
    elif typ == params.vec3:
        return MultiWidget(parent, (float, float, float), curvalue, client)
    elif typ == params.nicosdev:
        return DeviceComboWidget(parent, curvalue, client)
    elif typ in (params.tacodev, params.tangodev, params.mailaddress,
                 params.subdir, params.relative_path, params.absolute_path):
        # XXX validate via regexp
        return EditWidget(parent, str, curvalue)
    elif typ == anytype:
        return ExprWidget(parent, curvalue)
    elif isinstance(typ, params.listof):
        return ListOfWidget(parent, typ.conv, curvalue, client)
    elif isinstance(typ, params.nonemptylistof):
        return ListOfWidget(parent, typ.conv, curvalue, client, nmin=1)
    elif isinstance(typ, params.dictof):
        return DictOfWidget(parent, typ.keyconv, typ.valconv, curvalue,
                            client)
    return MissingWidget(parent, curvalue)


class AnnotatedWidget(QWidget):

    def __init__(self, parent, inner, annotation):
        QWidget.__init__(self, parent)
        layout = self._layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._inner = inner
        self.connect(inner, SIGNAL('dataChanged'),
                     lambda: self.emit(SIGNAL('dataChanged')))
        self.connect(inner, SIGNAL('valueChosen'),
                     lambda val: self.emit(SIGNAL('valueChosen'), val))
        layout.addWidget(inner)
        layout.addWidget(QLabel(annotation, parent))
        self.setLayout(layout)

    def getValue(self):
        return self._inner.getValue()

    def setFocus(self):
        self._inner.setFocus()


class MultiWidget(QWidget):

    def __init__(self, parent, types, curvalue, client):
        QWidget.__init__(self, parent)
        layout = self._layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._widgets = []
        for (typ, val) in zip(types, curvalue):
            widget = create(self, typ, val, client=client)
            self._widgets.append(widget)
            self.connect(widget, SIGNAL('dataChanged'),
                         lambda: self.emit(SIGNAL('dataChanged')))
            layout.addWidget(widget)
        self.setLayout(layout)

    def getValue(self):
        return tuple(w.getValue() for w in self._widgets)


class LimitsWidget(MultiWidget):

    def __init__(self, parent, curvalue, client):
        MultiWidget.__init__(self, parent, (float, float), curvalue, client)
        self._layout.insertWidget(0, QLabel('from', self))
        self._layout.insertWidget(2, QLabel('to', self))


class ComboWidget(QComboBox):

    def __init__(self, parent, values, curvalue):
        QComboBox.__init__(self, parent)
        self._values = sorted(values, key=str)
        self._textvals = list(map(str, self._values))
        self.addItems(self._textvals)
        if curvalue in self._values:
            self.setCurrentIndex(self._values.index(curvalue))
        self.connect(self, SIGNAL('currentIndexChanged(int)'),
                     lambda idx: self.emit(SIGNAL('dataChanged')))

    def getValue(self):
        return self._values[self._textvals.index(self.currentText())]


class ButtonWidget(QWidget):

    def __init__(self, parent, values):
        QWidget.__init__(self, parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._values = {}
        for value in values:
            btn = QPushButton(str(value), self)
            self._values[btn] = value
            btn.clicked.connect(self.on_button_pressed)
            layout.addWidget(btn)
        self.setLayout(layout)

    def on_button_pressed(self):
        self.emit(SIGNAL('valueChosen'), self._values[self.sender()])

    def getValue(self):
        return None


class EditWidget(QLineEdit):

    def __init__(self, parent, typ, curvalue, fmtstr='%.4g', minmax=None):
        QLineEdit.__init__(self, parent)
        self._typ = typ
        if typ is float:
            val = QDoubleValidator(self)
            if minmax:
                val.setRange(minmax[0], minmax[1]
                             if minmax[1] is not None else float('inf'))
            self.setValidator(val)
            self.setText(fmtstr % curvalue)
        elif typ is int:
            val = QIntValidator(self)
            if minmax:
                val.setRange(minmax[0], minmax[1])
            self.setValidator(val)
            self.setText(str(curvalue))
        else:
            self.setText(str(curvalue))
        self.connect(self, SIGNAL('textChanged(const QString &)'),
                     lambda txt: self.emit(SIGNAL('dataChanged')))
        self.connect(self, SIGNAL('returnPressed()'),
                     lambda: self.emit(SIGNAL('valueChosen'), self.text()))

    def getValue(self):
        return self._typ(self.text())


class SpinBoxWidget(QSpinBox):

    def __init__(self, parent, curvalue, minmax, fmtstr='%.4g'):
        QSpinBox.__init__(self, parent)
        self.setRange(minmax[0], minmax[1])
        self.setValue(curvalue)
        self.connect(self, SIGNAL('valueChanged(int)'),
                     lambda val: self.emit(SIGNAL('dataChanged')))

    def getValue(self):
        return self.value()


class ExprWidget(QLineEdit):

    def __init__(self, parent, curvalue):
        QLineEdit.__init__(self, parent)
        self.setText(cache_dump(curvalue))
        self.connect(self, SIGNAL('textChanged(const QString &)'),
                     lambda txt: self.emit(SIGNAL('dataChanged')))

    def getValue(self):
        return cache_load(self.text())


class CheckWidget(QWidget):

    def __init__(self, parent, inner, curvalue, client):
        QWidget.__init__(self, parent)
        layout = self._layout = QHBoxLayout()
        self.checkbox = QCheckBox(self)
        if curvalue is not None:
            self.checkbox.setCheckState(Qt.Checked)
        if curvalue is None:
            curvalue = inner()  # generate a dummy value
        self.inner_widget = create(self, inner, curvalue, client=client)
        self.inner_widget.setEnabled(self.checkbox.isChecked())
        self.connect(self.inner_widget, SIGNAL('dataChanged'),
                     lambda: self.emit(SIGNAL('dataChanged')))
        layout.addWidget(self.checkbox)
        layout.addWidget(self.inner_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.connect(self.checkbox, SIGNAL('stateChanged(int)'),
                     self.on_checkbox_stateChanged)
        self.setLayout(layout)

    def on_checkbox_stateChanged(self, state):
        self.inner_widget.setEnabled(state == Qt.Checked)
        self.emit(SIGNAL('dataChanged'))

    def getValue(self):
        if self.checkbox.isChecked():
            return self.inner_widget.getValue()
        return None


class MissingWidget(QLabel):

    def __init__(self, parent, curvalue):
        QLabel.__init__(self, parent)
        self.setText('(editing impossible)')
        self._value = curvalue

    def getValue(self):
        return self._value


class DeviceComboWidget(QComboBox):

    def __init__(self, parent, curvalue, client,
                 needs_class='nicos.core.device.Device'):
        QComboBox.__init__(self, parent, editable=True)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        if client:
            devs = client.getDeviceList(needs_class)
            self.addItems(devs)
            try:
                index = devs.index(curvalue)
                self.setCurrentIndex(index)
            except ValueError:
                self.setEditText(curvalue)
        else:
            self.setEditText(curvalue)
        self.editTextChanged.connect(lambda: self.emit(SIGNAL('dataChanged')))

    def getValue(self):
        return self.currentText()


class ItemsWidget(QScrollArea):

    allow_reorder = True

    def __init__(self, parent, nmin):
        QScrollArea.__init__(self, parent)
        self.setWidgetResizable(True)
        self.frame = QFrame(self)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.addBtn = QPushButton(QIcon(':/add'), '', self.frame)
        self.addBtn.clicked.connect(self.on_addBtn_clicked)
        self.addBtn.setSizePolicy(
            QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred))
        self.layout.addWidget(self.addBtn)
        self.layout.addStretch()
        self.frame.setLayout(self.layout)
        self.setWidget(self.frame)
        self.items = []
        self.nmin = nmin

    def insertItem(self, *widgets):
        item = QWidget(self.frame)
        item._widgets = widgets
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        for widget in widgets:
            layout.addWidget(widget)
        if self.allow_reorder:
            btn = QPushButton(QIcon(':/up'), '', item)
            btn._item = item
            btn.clicked.connect(self.on_upBtn_clicked)
            layout.addWidget(btn)
            btn = QPushButton(QIcon(':/down'), '', item)
            btn._item = item
            btn.clicked.connect(self.on_downBtn_clicked)
            layout.addWidget(btn)
        btn = QPushButton(QIcon(':/remove'), '', item)
        btn._item = item
        btn.clicked.connect(self.on_removeBtn_clicked)
        layout.addWidget(btn)
        item.setLayout(layout)
        self.layout.insertWidget(self.layout.count()-2, item)
        self.items.append(item)

    def on_addBtn_clicked(self):
        self.insertItem(*self.createItem())
        self.emit(SIGNAL('dataChanged'))

    def on_removeBtn_clicked(self):
        if len(self.items) <= self.nmin:
            return
        item = self.sender()._item
        index = self.items.index(item)
        del self.items[index]
        self.layout.takeAt(index).widget().deleteLater()
        self.emit(SIGNAL('dataChanged'))

    def on_upBtn_clicked(self):
        item = self.sender()._item
        index = self.items.index(item)
        if index <= 0:
            return
        self._swapItems(index - 1)

    def on_downBtn_clicked(self):
        item = self.sender()._item
        index = self.items.index(item)
        if index >= len(self.items) - 1:
            return
        self._swapItems(index)

    def _swapItems(self, firstindex):
        item1 = self.items[firstindex]
        item2 = self.items[firstindex+1]
        self.layout.takeAt(firstindex)
        self.layout.takeAt(firstindex)  # moved up one
        self.items[firstindex:firstindex+2] = [item2, item1]
        self.layout.insertWidget(firstindex, item2)
        self.layout.insertWidget(firstindex+1, item1)
        self.emit(SIGNAL('dataChanged'))


class ListOfWidget(ItemsWidget):

    def __init__(self, parent, inner, curvalue, client, nmin=0):
        ItemsWidget.__init__(self, parent, nmin)
        self.inner = inner
        self.client = client

        for item in curvalue:
            self.insertItem(*self.createItem(item))

    def createItem(self, value=None):
        if value is None:
            value = self.inner()
        widget = create(self, self.inner, value, client=self.client)
        self.connect(widget, SIGNAL('dataChanged'),
                     lambda: self.emit(SIGNAL('dataChanged')))
        return (widget,)

    def getValue(self):
        return [w._widgets[0].getValue() for w in self.items]


class DictOfWidget(ItemsWidget):

    allow_reorder = False

    def __init__(self, parent, keytype, valtype, curvalue, client, nmin=0):
        ItemsWidget.__init__(self, parent, nmin)
        self.keytype = keytype
        self.valtype = valtype
        self.client = client

        for keyval in iteritems(curvalue):
            self.insertItem(*self.createItem(keyval))

    def createItem(self, keyval=None):
        if keyval is None:
            key = self.keytype()
            val = self.valtype()
        else:
            key, val = keyval  # pylint: disable=W0633
        keywidget = create(self, self.keytype, key, client=self.client)
        self.connect(keywidget, SIGNAL('dataChanged'),
                     lambda: self.emit(SIGNAL('dataChanged')))
        valwidget = create(self, self.valtype, val, client=self.client)
        self.connect(valwidget, SIGNAL('dataChanged'),
                     lambda: self.emit(SIGNAL('dataChanged')))
        return (keywidget, QLabel('=>', self), valwidget)

    def getValue(self):
        return dict((w._widgets[0].getValue(),
                     w._widgets[2].getValue()) for w in self.items)
