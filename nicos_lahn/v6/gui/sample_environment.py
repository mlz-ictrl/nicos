# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Facundo Silberstein <facundosilberstein@cnea.gob.ar>
#   Leonardo J. Ibáñez <leonardoibanez@cnea.gob.ar>
# *****************************************************************************
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, ScriptExecQuestion
from nicos.utils import findResource
from nicos.guisupport.qt import QIcon, pyqtSlot, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSlider, QDoubleSpinBox, QPushButton, QButtonGroup
from nicos.utils.files import iterSetups
from nicos.core.sessions.setups import make_configdata
import os


class Sample_Environment(Panel):
    panelName = 'Sample Environment'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_lahn/v6/gui/sample_environment.ui'))
        self.current_status = None
        self.btnRun.setIcon(QIcon(':/continue'))
        self.btnRun.clicked.connect(self.on_start_clicked)

    def load_configuration(self):
        self.clear_existing_widgets()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        setups_path = os.path.join(current_dir, "..", "setups")
        setups_path = os.path.normpath(setups_path)
        all_setups_dict = dict(iterSetups([setups_path]))
        filepath = all_setups_dict['config_secop']
        configdata = make_configdata(filepath, all_setups_dict, set())
        items = list(configdata('config_secop.secop_devices').items())
        # Node
        node_name = items[0][0]
        self.node_label.setText(node_name)
        self.node_label.setAlignment(Qt.AlignCenter)
        font = self.node_label.font()
        font.setBold(True)
        font.setUnderline(True)
        self.node_label.setFont(font)
        # Modules
        row = 0
        # SECoP Moveable list
        self.secop_moveable = []
        for module_name, module_info in items[1:]:
            if len(module_info) > 1:
                module_limits = module_info.get("limits")
                module_target = module_info.get("target")
                module_unit = module_info.get("unit")
                self.mod_layout = QHBoxLayout()
                self.secop_moveable.append({
                    'name': module_name,
                    'target': module_target
                })
                if module_limits is not None and module_target is not None:
                    self.DeviceHasSlider(
                        module_name, module_limits, module_target, module_unit)
                elif module_limits is None and module_target is not None:
                    if isinstance(module_target, (int, float)):
                        self.DeviceHasSpinBox(
                            module_name, module_target, module_unit)
                    elif isinstance(module_target, str):
                        self.DeviceHasSwitch(module_name)
                self.nod_layout.addLayout(self.mod_layout, row, 0)
                row += 1

    def DeviceHasSlider(self, name, limits, target, unit):
        mod_value_label = QLabel()
        mod_slider = QSlider(Qt.Horizontal)
        mod_slider.setRange(int(100 * limits[0]), int(100 * limits[1]))
        last_value = getattr(self, f"{name}_last_position", None)
        if last_value is not None:
            mod_slider.setValue(last_value)
            mod_value_label.setText(str(last_value / 100))
        else:
            mod_slider.setValue(int(100 * target))
            mod_value_label.setText(f"{int(target/100)}")

        mod_slider.valueChanged.connect(
            lambda value: mod_value_label.setText(str(value / 100)))
        self.mod_layout.addWidget(QLabel(name))
        self.mod_layout.addWidget(mod_slider)
        self.mod_layout.addWidget(mod_value_label)
        self.mod_layout.addWidget(QLabel(unit))

        setattr(self, f"{name}_slider", mod_slider)
        setattr(self, f"{name}_value_label", mod_value_label)

    def DeviceHasSpinBox(self, name, target, unit):
        mod_doubleSpinBox = QDoubleSpinBox()
        mod_doubleSpinBox.setRange(-9000, 9000)

        last_value = getattr(self, f"{name}_last_num", None)
        if last_value is not None:
            mod_doubleSpinBox.setValue(last_value)
        else:
            mod_doubleSpinBox.setValue(float(target))
        self.mod_layout.addWidget(QLabel(name))
        self.mod_layout.addWidget(mod_doubleSpinBox)
        self.mod_layout.addWidget(QLabel(unit))

        setattr(self, f"{name}_doubleSpinBox", mod_doubleSpinBox)

    def DeviceHasSwitch(self, name):
        mod_setok = QPushButton("ok")
        mod_setoff = QPushButton("off")
        mod_setok.setCheckable(True)
        mod_setoff.setCheckable(True)
        mod_switch = QButtonGroup(self)
        mod_switch.setExclusive(True)
        mod_switch.addButton(mod_setok)
        mod_switch.addButton(mod_setoff)
        mod_setoff.setChecked(True)

        last_state = getattr(self, f"{name}_last_state", None)
        if last_state == "ok":
            mod_setok.setChecked(True)
        elif last_state == "off" or last_state is None:
            mod_setoff.setChecked(True)

        self.mod_layout.addWidget(QLabel(name))
        self.mod_layout.addWidget(mod_setok)
        self.mod_layout.addWidget(mod_setoff)

        setattr(self, f"{name}_ok", mod_setok)
        setattr(self, f"{name}_off", mod_setoff)

    def clear_existing_widgets(self):
        for i in reversed(range(self.nod_layout.count())):
            item = self.nod_layout.itemAt(i)
            if item and item.layout():
                for j in reversed(range(item.layout().count())):
                    widget = item.layout().itemAt(j).widget()
                    if widget:
                        widget.setParent(None)
                        widget.deleteLater()
                self.nod_layout.removeItem(item)
                item.layout().deleteLater()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_configuration()

    def hideEvent(self, event):
        super().hideEvent(event)
        for module_moveable in self.secop_moveable:
            name = module_moveable['name']
            slider = getattr(self, f"{name}_slider", None)
            spinbox = getattr(self, f"{name}_doubleSpinBox", None)
            ok_button = getattr(self, f"{name}_ok", None)
            off_button = getattr(self, f"{name}_off", None)
            if slider:
                setattr(self, f"{name}_last_position", slider.value())
            elif spinbox:
                setattr(self, f"{name}_last_num", spinbox.value())
            elif ok_button and off_button:
                if ok_button.isChecked():
                    setattr(self, f"{name}_last_state", "ok")
                elif off_button.isChecked():
                    setattr(self, f"{name}_last_state", "off")

    def updateStatus(self, status, exception=False):
        self.current_status = status

    @pyqtSlot()
    def on_start_clicked(self):
        code = []
        user_entry = []
        for module_moveable in self.secop_moveable:
            dev_name = module_moveable['name']
            dev_target = module_moveable['target']
            if isinstance(dev_target, (int, float)):
                if hasattr(self, f"{dev_name}_value_label"):
                    dev_label = getattr(self, f"{dev_name}_value_label")
                    dev_value = dev_label.text()
                elif hasattr(self, f"{dev_name}_doubleSpinBox"):
                    dev_spinbox = getattr(self, f"{dev_name}_doubleSpinBox")
                    dev_value = dev_spinbox.value()
            elif hasattr(self, f"{dev_name}_ok"):
                dev_okbtn = getattr(self, f"{dev_name}_ok")
                if dev_okbtn.isChecked():
                    dev_value = "'on'"
                else:
                    dev_value = "'off'"
            user_entry.extend([dev_name, dev_value])
        user_str = ", ".join(str(x) for x in user_entry)
        code.append(f'maw({user_str})')
        code.append('read()')
        self.execScript('\n'.join(code))

    def execScript(self, script):
        action = 'queue'
        if self.current_status != 'idle':
            qwindow = ScriptExecQuestion()
            result = qwindow.exec()
            if result == QMessageBox.Cancel:
                return
            elif result == QMessageBox.Apply:
                action = 'execute'
        if action == 'queue':
            self.client.run(script)
        else:
            self.client.tell('exec', script)
