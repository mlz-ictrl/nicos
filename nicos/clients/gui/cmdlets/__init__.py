# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS GUI command input widgets."""

from nicos.clients.gui.utils import loadUi
from nicos.guisupport.colors import colors
from nicos.guisupport.qt import QAbstractSpinBox, QWidget, pyqtSignal, pyqtSlot
from nicos.guisupport.typedvalue import DeviceParamEdit
from nicos.guisupport.utils import DoubleValidator, setBackgroundColor
from nicos.utils import findResource, formatDuration


def isFloat(ctl, minval=None, maxval=None, conv=float):
    try:
        v = conv(ctl.text())
    except ValueError:
        return False
    if minval is not None and v < minval:
        return False
    if maxval is not None and v > maxval:
        return False
    return True


def isInt(ctl, minval=None, maxval=None):
    return isFloat(ctl, minval, maxval, int)


class Cmdlet(QWidget):

    name = ''
    category = ''

    cmdletUp = pyqtSignal()
    cmdletDown = pyqtSignal()
    cmdletRemove = pyqtSignal()
    valueModified = pyqtSignal()

    def __init__(self, parent, client, options, uifile):
        self.client = client
        self.options = options
        QWidget.__init__(self, parent)
        loadUi(self, uifile)
        loadUi(self.buttons, 'cmdlets/buttons.ui')
        self.buttons.upBtn.clicked.connect(self.cmdletUp)
        self.buttons.downBtn.clicked.connect(self.cmdletDown)
        self.buttons.delBtn.clicked.connect(self.cmdletRemove)

    def removeSelf(self):
        self.parent().layout().removeWidget(self)
        self.hide()

    def changed(self, *args):
        """Should be called whenever any value in the cmdlet changes."""
        self.valueModified.emit()

    def getValues(self):
        """Return a dict with the values of the cmdlet.

        Values should have a name that is the same for the same logical
        value in multiple cmdlets, e.g. "dev" for the device in a command.
        """
        return {}

    def _getDeviceList(self, special_clause=''):
        """Helper for getting a list of devices for manipulation."""
        exp = getattr(self.parent(), 'expertmode', False)
        if exp:
            clause = special_clause
        else:
            clause = ('(dn in session.explicit_devices or '
                      '("nicos.core.mixins.AutoDevice" in d.classes and '
                      'dn.split(".")[0] in session.explicit_devices))')
            if special_clause:
                clause += ' and ' + special_clause
        # special construction to get AutoDevices like slit.centerx which is
        # useful to make scans over
        return self.client.getDeviceList('nicos.core.device.Moveable',
                                         only_explicit=False,
                                         special_clause=clause)

    def _getDeviceRepr(self, devname):
        """Return bare ``dev`` if the device is in the NICOS user namespace,
        else ``'dev'`` in quotes.
        """
        if self.client.eval(devname, None) is None:
            return repr(devname)
        return devname

    def _setDevice(self, values):
        """Helper for setValues for setting a device combo box."""
        if 'dev' in values:
            idx = self.device.findText(values['dev'])
            if idx > -1:
                self.device.setCurrentIndex(idx)

    def setValues(self, values):
        """Set values of the cmdlet with values from the argument.

        Unknown values must be ignored.
        """

    def markValid(self, ctl, condition):
        """Return boolean condition, and also mark the offending widget.

        For use in isValid().
        """
        if condition:
            setBackgroundColor(ctl, colors.palette.window().color())
        else:
            setBackgroundColor(ctl, colors.invalid)
        if isinstance(ctl, QAbstractSpinBox):
            # also mark the inner line-edit
            return self.markValid(ctl.lineEdit(), condition)
        return condition

    def isValid(self):
        """Check if all entered data is valid.

        This method can change widget styles to indicate invalid data with
        the markValid() method if wanted.
        """
        return True

    def generate(self):
        """Generate code for the commandlet.

        *mode* is 'python' or 'simple'.

        Should generate a string of lines, complete with newlines.
        """
        return ''


class Move(Cmdlet):

    name = 'Move'
    category = 'Device'

    def __init__(self, parent, client, options):
        Cmdlet.__init__(self, parent, client, options, 'cmdlets/move.ui')
        self.multiList.entryAdded.connect(self.on_entryAdded)
        self.multiList.uifile = findResource('nicos/clients/gui/cmdlets/move_one.ui')
        self.waitBox.stateChanged.connect(self.changed)

    def on_entryAdded(self, entry):
        def on_device_change(text):
            entry.target.dev = text
            self.changed()
        entry.device.addItems(self._getDeviceList())
        on_device_change(entry.device.currentText())
        entry.device.currentIndexChanged['QString'].connect(on_device_change)
        entry.target.setClient(self.client)
        entry.target.valueModified.connect(self.changed)

    def _setDevice(self, values):
        """Helper for setValues for setting a device combo box."""
        if 'dev' in values:
            idx = self.multiList.entry(0).device.findText(values['dev'])
            if idx > -1:
                self.multiList.entry(0).device.setCurrentIndex(idx)

    def getValues(self):
        return {'dev':    self.multiList.entry(0).device.currentText(),
                'moveto': self.multiList.entry(0).target.getValue()}

    def setValues(self, values):
        self._setDevice(values)
        if 'moveto' in values:
            self.multiList.entry(0).target.setValue(values['moveto'])

    def generate(self):
        cmd = 'maw' if self.waitBox.isChecked() else 'move'
        return cmd + '(' + ', '.join('%s, %r' % (
            self._getDeviceRepr(frm.device.currentText()), frm.target.getValue())
            for frm in self.multiList.entries()) + ')'


class PresetHelper:
    def _addPresets(self, combo):
        self._presetkeys = {'seconds': 't', 'minutes': 't'}
        for preset in self.options.get('add_presets', []):
            key, name = preset[:2]
            self._presetkeys[name] = key
            combo.addItem(name)

    def _getPreset(self, values):
        presetvalue, presetunit = values['preset'], values['presetunit']
        presetkey = self._presetkeys[presetunit]
        if presetunit == 'minutes':
            presetvalue *= 60
        return f'{presetkey}={presetvalue}'


class Count(PresetHelper, Cmdlet):

    name = 'Count'
    category = 'Scan'

    def __init__(self, parent, client, options):
        Cmdlet.__init__(self, parent, client, options, 'cmdlets/count.ui')
        self._addPresets(self.presetunit)
        self.preset.valueChanged.connect(self.changed)
        self.presetunit.currentTextChanged.connect(self.changed)

    def getValues(self):
        return {'preset': self.preset.value(),
                'presetunit': self.presetunit.currentText()}

    def setValues(self, values):
        if 'preset' in values:
            self.preset.setValue(values['preset'])
        if 'presetunit' in values:
            self.presetunit.setCurrentText(values['presetunit'])

    def isValid(self):
        return self.markValid(self.preset, self.preset.value() > 0)

    def generate(self):
        preset = self._getPreset(self.getValues())
        return f'count({preset})'


class CommonScan(PresetHelper, Cmdlet):

    cmdname = ''
    uiName = ''

    def __init__(self, parent, client, options):
        Cmdlet.__init__(self, parent, client, options, self.uiName)
        self._addPresets(self.presetunit)
        self.device.addItems(self._getDeviceList())
        self.on_device_change(self.device.currentText())
        self.device.currentIndexChanged[str].connect(self.on_device_change)
        self.start.setValidator(DoubleValidator(self))
        self.step.setValidator(DoubleValidator(self))
        self.start.textChanged.connect(self.on_range_change)
        self.step.textChanged.connect(self.on_range_change)
        self.numpoints.valueChanged.connect(self.on_range_change)
        self.preset.valueChanged.connect(self.changed)
        self.presetunit.currentTextChanged.connect(self.changed)
        self.contBox.toggled.connect(self.changed)

    def on_device_change(self, text):
        unit = self.client.getDeviceParam(text, 'unit')
        self.unit1.setText(unit or '')
        self.unit2.setText(unit or '')
        self.changed()

    def getValues(self):
        return {'dev': self.device.currentText(),
                'scanstart': self.start.text(),
                'scanstep': self.step.text(),
                'scanpoints': self.numpoints.value(),
                'scancont': self.contBox.isChecked(),
                'preset': self.preset.value(),
                'presetunit': self.presetunit.currentText()}

    def setValues(self, values):
        self._setDevice(values)
        if 'scanstart' in values:
            self.start.setText(values['scanstart'])
        if 'scanstep' in values:
            self.step.setText(values['scanstep'])
        if 'scanpoints' in values:
            self.numpoints.setValue(values['scanpoints'])
        if 'scancont' in values:
            self.contBox.setChecked(values['scancont'])
        if 'preset' in values:
            self.preset.setValue(values['preset'])
        if 'presetunit' in values:
            self.presetunit.setCurrentText(values['presetunit'])

    def isValid(self):
        # NOTE: cannot use "return markValid() and markValid() and ..." because
        # that short-circuits evaluation and therefore skips marking all but the
        # first invalid control
        valid = [
            self.markValid(self.start, isFloat(self.start)),
            self.markValid(self.step, isFloat(self.step)),
            self.markValid(self.preset, self.preset.value() > 0),
        ]
        return all(valid)

    def generate(self):
        values = self.getValues()
        devrepr = self._getDeviceRepr(values['dev'])

        if values['scancont']:
            start, end, speed, delta = self._getContParams(values)
            return f'contscan({devrepr}, {start}, {end}, {speed}, {delta})'

        preset = self._getPreset(values)
        return f'{self.cmdname}({devrepr}, {values["scanstart"]}, ' \
            f'{values["scanstep"]}, {values["scanpoints"]}, {preset})'


class Scan(CommonScan):

    name = 'Scan'
    category = 'Scan'
    cmdname = 'scan'
    uiName = 'cmdlets/scan.ui'

    def on_range_change(self, *args):
        try:
            start = float(self.start.text())
            step = float(self.step.text())
        except ValueError:
            endpos = ''
        else:
            numpoints = self.numpoints.value()
            endpos = '%.3f %s' % (start + (numpoints-1)*step, self.unit1.text())
        self.endPos.setText(endpos)
        self.changed()

    def _getContParams(self, values):
        start, step, npoints, ctime = (float(values['scanstart']),
                                       float(values['scanstep']),
                                       float(values['scanpoints']),
                                       values['preset'])
        end = start + (npoints - 1) * step
        return start, end, abs(end - start) / npoints / ctime, ctime


class CScan(CommonScan):

    name = 'Centered Scan'
    category = 'Scan'
    cmdname = 'cscan'
    uiName = 'cmdlets/cscan.ui'

    def on_range_change(self, *args):
        numpoints = self.numpoints.value()
        try:
            start = float(self.start.text())
            step = float(self.step.text())
        except ValueError:
            edgepos = ''
        else:
            edgepos = '%.3f - %.3f %s' % (start - numpoints*step,
                                          start + numpoints*step,
                                          self.unit1.text())
        self.edgePos.setText(edgepos)
        self.totalPoints.setText('Total: %d points' % (2 * numpoints + 1))
        self.changed()

    def _getContParams(self, values):
        center, step, npoints, ctime = (float(values['scanstart']),
                                        float(values['scanstep']),
                                        float(values['scanpoints']),
                                        values['preset'])
        start = center - npoints * step
        end = center + npoints * step
        return start, end, abs(end - start) / (2*npoints + 1) / ctime, ctime


class Center(CommonScan):

    name = 'Center/Move on fit maximum'
    category = 'Scan'
    cmdname = 'center'
    uiName = 'cmdlets/cscan.ui'

    def __init__(self, parent, client, options):
        CommonScan.__init__(self, parent, client, options)
        self.contBox.hide()
        self.label.setText('<b>Center</b> device:')

    def on_range_change(self, *args):
        numpoints = self.numpoints.value()
        try:
            start = float(self.start.text())
            step = float(self.step.text())
        except ValueError:
            edgepos = ''
        else:
            edgepos = '%.3f - %.3f %s' % (start - numpoints*step,
                                          start + numpoints*step,
                                          self.unit1.text())
        self.edgePos.setText(edgepos)
        self.totalPoints.setText('Total: %d points' % (2 * numpoints + 1))
        self.changed()

    def _getContParams(self, values):
        center, step, npoints, ctime = (float(values['scanstart']),
                                        float(values['scanstep']),
                                        float(values['scanpoints']),
                                        values['preset'])
        start = center - npoints * step
        end = center + npoints * step
        return start, end, abs(end - start) / (2*npoints + 1) / ctime, ctime


class TimeScan(PresetHelper, Cmdlet):

    name = 'Time scan'
    category = 'Scan'

    def __init__(self, parent, client, options):
        Cmdlet.__init__(self, parent, client, options, 'cmdlets/timescan.ui')
        self._addPresets(self.presetunit)
        self.preset.valueChanged.connect(self.changed)
        self.presetunit.currentTextChanged.connect(self.changed)

    def on_infBox_toggled(self, on):
        self.numpoints.setEnabled(not on)
        self.changed()

    def getValues(self):
        return {'scanpoints': self.numpoints.value(),
                'countinf': self.infBox.isChecked(),
                'preset': self.preset.value(),
                'presetunit': self.presetunit.currentText()}

    def setValues(self, values):
        if 'scanpoints' in values:
            self.numpoints.setValue(values['scanpoints'])
        if 'countinf' in values:
            self.infBox.setChecked(bool(values['countinf']))
        if 'preset' in values:
            self.preset.setValue(values['preset'])
        if 'presetunit' in values:
            self.presetunit.setCurrentText(values['presetunit'])

    def isValid(self):
        return self.markValid(self.preset, self.preset.value() > 0)

    def generate(self):
        values = self.getValues()
        preset = self._getPreset(values)
        npoints = -1 if values['countinf'] else values['scanpoints']
        return f'timescan({npoints}, {preset})'


class ContScan(Cmdlet):

    name = 'Continuous Scan'
    category = 'Scan'

    def __init__(self, parent, client, options):
        Cmdlet.__init__(self, parent, client, options, 'cmdlets/contscan.ui')
        self.device.addItems(self._getDeviceList('hasattr(d, "speed")'))
        self.on_device_change(self.device.currentText())
        self.device.currentIndexChanged[str].connect(self.on_device_change)
        self.start.setValidator(DoubleValidator(self))
        self.stop.setValidator(DoubleValidator(self))
        self.speed.setValidator(DoubleValidator(self))
        self.delta.setValidator(DoubleValidator(self))
        self.start.textChanged.connect(self.on_range_change)
        self.stop.textChanged.connect(self.on_range_change)
        self.speed.textChanged.connect(self.on_range_change)
        self.delta.textChanged.connect(self.on_range_change)

    def on_range_change(self):
        try:
            rng = abs(float(self.start.text()) - float(self.stop.text()))
            secs = rng / float(self.speed.text())
            pnts = int(secs / float(self.delta.text()))
            self.totalLabel.setText('Total: %d points, %s' %
                                    (pnts, formatDuration(secs)))
        except (ValueError, ArithmeticError):
            self.totalLabel.setText('Total:')
        self.changed()

    def on_device_change(self, text):
        unit = self.client.getDeviceParam(text, 'unit')
        value = self.client.getDeviceParam(text, 'value')
        fmtstr = self.client.getDeviceParam(text, 'fmtstr')
        try:
            self.start.setText(fmtstr % value)
        except Exception:
            pass
        self.unit1.setText(unit or '')
        self.unit2.setText(unit or '')
        self.unit3.setText((unit or '') + '/second')
        self.changed()

    def getValues(self):
        return {'dev': self.device.currentText(),
                'scanstart': self.start.text(),
                'scanend': self.stop.text(),
                'devspeed': self.speed.text(),
                'preset': float(self.delta.text())}

    def setValues(self, values):
        self._setDevice(values)
        if 'scanstart' in values:
            self.start.setText(values['scanstart'])
        if 'scanend' in values:
            self.stop.setText(values['scanend'])
        if 'devspeed' in values:
            self.speed.setText(values['devspeed'])
        if 'preset' in values:
            self.delta.setText(str(values['preset']))

    def isValid(self):
        valid = [
            self.markValid(self.start, isFloat(self.start)),
            self.markValid(self.stop, isFloat(self.stop)),
            self.markValid(self.speed, isFloat(self.speed, 0.00001)),
            self.markValid(self.delta, isFloat(self.delta, 0.05)),
        ]
        return all(valid)

    def generate(self):
        values = self.getValues()
        values['dev'] = self._getDeviceRepr(values['dev'])
        return 'contscan(%(dev)s, %(scanstart)s, %(scanend)s, %(devspeed)s, ' \
               '%(preset)s)' % values


class Sleep(Cmdlet):

    name = 'Sleep'
    category = 'Other'

    def __init__(self, parent, client, options):
        Cmdlet.__init__(self, parent, client, options, 'cmdlets/sleep.ui')
        self.seconds.valueChanged.connect(self.changed)

    def getValues(self):
        return {'sleeptime': self.seconds.value()}

    def setValues(self, values):
        if 'sleeptime' in values:
            self.seconds.setValue(values['sleeptime'])

    def isValid(self):
        return self.markValid(self.seconds, self.seconds.value() > 0)

    def generate(self):
        return 'sleep(%(sleeptime)s)' % self.getValues()


class Configure(Cmdlet):

    name = 'Configure'
    category = 'Device'

    def __init__(self, parent, client, options):
        Cmdlet.__init__(self, parent, client, options, 'cmdlets/configure.ui')
        self.paraminfo = {}
        self.paramvalues = {}
        self.target = DeviceParamEdit(self)
        self.target.setClient(self.client)
        self.target.valueModified.connect(self.changed)
        self.hlayout.insertWidget(5, self.target)
        self.device.addItems(self._getDeviceList())
        self.on_device_change(self.device.currentText())
        self.device.currentIndexChanged[str].connect(self.on_device_change)
        self.parameter.currentIndexChanged[str].connect(
            self.on_parameter_change)

    def on_device_change(self, text):
        self.paraminfo = self.client.getDeviceParamInfo(text)
        self.paramvalues = dict(self.client.getDeviceParams(text))
        self.parameter.clear()
        self.parameter.addItems(sorted(p for p in self.paraminfo
                                       if self.paraminfo[p]['settable'] and
                                       self.paraminfo[p]['userparam']))
        self.target.dev = text
        self.on_parameter_change(self.parameter.currentText())
        self.changed()

    def on_parameter_change(self, text):
        self.target.param = text
        self.changed()

    def getValues(self):
        return {'dev': self.device.currentText(),
                'param': self.parameter.currentText(),
                'paramvalue': self.target.getValue()}

    def setValues(self, values):
        self._setDevice(values)
        if 'param' in values:
            idx = self.parameter.findText(values['param'])
            if idx > -1:
                self.parameter.setCurrentIndex(idx)
        # DeviceValueEdit doesn't support setValue (yet)
        # if 'paramvalue' in values:
        #     self.target.setValue(values['paramvalue'])

    def isValid(self):
        return self.markValid(self.target, True)

    def generate(self):
        values = self.getValues()
        values['dev'] = self._getDeviceRepr(values['dev'])
        return 'set(%(dev)s, %(param)r, %(paramvalue)r)' % values


class NewSample(Cmdlet):

    name = 'New sample'
    category = 'Other'

    def __init__(self, parent, client, options):
        Cmdlet.__init__(self, parent, client, options, 'cmdlets/sample.ui')
        self.samplename.textChanged.connect(self.changed)

    def getValues(self):
        return {'samplename': self.samplename.text()}

    def setValues(self, values):
        if 'samplename' in values:
            self.samplename.setText(values['samplename'])

    def generate(self):
        return 'NewSample(%(samplename)r)' % self.getValues()


all_cmdlets = {}
all_categories = {}


def register(cmdlet, priority=None, cat_priority=None):
    """Register cmdlets to the pool of commandlets.

    * ``priority`` (default None) -- the lower this is the further up in the
    category the cmdlet will be listed. Within the same priority the cmdlets
    are kept in insertion order. If a cmdlet of a subclass is registered the
    old cmdlet is overridden, if it has the same priority. If the priority
    differs it is moved to the end of the new priority.
    Default priority is treated as the priority of the parent class or 100 if
    there is no parent class registered yet.

    * ``cat_priority`` (default None) -- register_category will be called with
    this value.
    """

    # search for commandlet or a parent class
    for prio, cmdlets in all_cmdlets.items():
        for i, old in enumerate(cmdlets):
            if issubclass(cmdlet, old):
                # replace if priority is the same
                if prio == priority or priority is None:
                    all_cmdlets[prio][i] = cmdlet  # pylint: disable=unnecessary-dict-index-lookup
                    register_category(cmdlet.category, cat_priority)
                    return
                # remove to add to the right priority later
                cmdlets.pop(i)

    if priority is None:
        priority = 100

    # actually register the commandlet
    all_cmdlets.setdefault(priority, []).append(cmdlet)
    register_category(cmdlet.category, cat_priority)


def deregister(cmdlet):
    for entry in all_cmdlets.values():
        if cmdlet in entry:
            entry.remove(cmdlet)
            return


def register_category(category, priority=None):
    """Register the category in the pool of cmdlet categories.

    * ``priority`` (default None) -- the lower this is the further to the left
    the category will be listed in the script- and cmdbuilder. Within one
    priority the insertion order is kept. If the category already exists in a
    different priority it is moved to the end of the new priority.
    Defaults to 100 if omitted and the category does not exist yet.
    """

    # check if the category already exists
    for prio, categories in all_categories.items():
        for i, old in enumerate(categories):
            if category == old:
                # already in the right priority
                if prio == priority or priority is None:
                    return
                # remove to add to the right priority later
                categories.pop(i)
                break

    if priority is None:
        priority = 100

    # actually register the category
    all_categories.setdefault(priority, []).append(category)


def get_priority_sorted_cmdlets():
    """Get a list of cmdlets which is ordered by priority and insertion order.
    This list is not sorted by categories.
    """
    cmdlets = []

    for key in sorted(all_cmdlets.keys()):
        cmdlets += all_cmdlets[key]

    return cmdlets


def get_priority_sorted_categories():
    """Get a list of all categories sorted by priority and insertion order."""
    categories = []

    for key in sorted(all_categories.keys()):
        categories += all_categories[key]

    return categories


for cmdlet in [Move, Count, Scan, CScan, TimeScan, ContScan,
               Sleep, Configure, NewSample, Center]:
    register(cmdlet)
