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
# Facundo Silberstein <facundosilberstein@cnea.gob.ar>
# *****************************************************************************
from nicos.commands import parallel_safe, usercommand
from nicos import session
import os

__all__ = ['CreateConfigSecop']

# Node name: current value of a SecNodeDevice


def GetNodeName(dev):
    current_value = dev.read()
    if isinstance(current_value, str):
        current_value = current_value.split(".")[0]
    return current_value


def GetModuleLimits(dev):
    if hasattr(dev, "doReadUserlimits"):
        module_limits = dev.doReadUserlimits()
    elif hasattr(dev, "doReadAbslimits"):
        module_limits = dev.doReadAbslimits()
    else:
        vt = getattr(dev, "valuetype", None)
        if vt is not None and hasattr(vt, "fr") and hasattr(vt, "to"):
            module_limits = (vt.fr, vt.to)
        else:
            module_limits = None
    return module_limits


def ListSecopDevices():
    secop_devices = []
    for devname in sorted(session.configured_devices):
        dev = session.devices[devname]
        if "SecNodeDevice" in dev.__class__.__name__:
            secop_devices.insert(0, {
                "name": GetNodeName(dev)
            })
        elif "Secop" in dev.__class__.__name__:
            module_info = {
                "name": dev.name,
                "description": dev.description,
            }
            if "SecopMoveable" in dev.__class__.__name__:
                module_info.update({
                    "limits": GetModuleLimits(dev),
                    "unit": dev.unit,
                    "target": dev.target
                })
            secop_devices.append(module_info)
    return secop_devices


@usercommand
@parallel_safe
def CreateConfigSecop(instrument="v6"):
    secop_dev = ListSecopDevices()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", instrument, "setups",
                             "config_secop.py")
    file_path = os.path.normpath(file_path)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(
            "description = 'SECoP devices'\n" +
            "group = 'configdata'\n")
        file.write("secop_devices = {\n")
        for device in secop_dev:
            name = device.get("name", "")
            description = device.get("description", "")
            limits = device.get("limits", None)
            unit = device.get("unit", "")
            target = device.get("target", None)
            file.write(f'\t"{name}": {{\n')
            if description:
                file.write(f'\t\t"description": "{description}",\n')
            if limits:
                file.write(f'\t\t"limits": {limits},\n')
            if unit:
                file.write(f'\t\t"unit": "{unit}",\n')
            if target is not None:
                if isinstance(target, (int, float)):
                    file.write(f'\t\t"target": {target},\n')
                else:
                    file.write(f'\t\t"target": "{target}",\n')
            file.write('\n\t},')
            file.write("\n")
        file.write("}\n")
