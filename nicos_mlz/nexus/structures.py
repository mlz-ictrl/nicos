# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

"""Some convenience methods to create structures for NeXus data writing."""

from nicos import session
from nicos.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceDataset, NXAttribute

seconds = NXAttribute('s', 'string')
counts = NXAttribute('counts', 'string')
nounit = NXAttribute('', 'string')
aa = NXAttribute('AA', 'string')
mm = NXAttribute('mm', 'string')
deg = NXAttribute('deg', 'string')

signal = NXAttribute(1, 'int')
axis0 = NXAttribute(0, 'int')
axis1 = NXAttribute(1, 'int')
axis2 = NXAttribute(2, 'int')
axis3 = NXAttribute(3, 'int')

mass_density = NXAttribute('g/cm^3', 'string')


def LocalContact():
    """Create local contact structure."""
    return {
        'role': ConstDataset('local_contact', 'string'),
        # TODO: split name from email address
        'name': DeviceDataset(session.experiment, 'localcontact'),
        'email': DeviceDataset(session.experiment, 'localcontact'),
    }


def User():
    """Create a NXuser structure."""
    return {
        'role': ConstDataset('principal_investigator', 'string'),
        # TODO: split name from email address
        'name': DeviceDataset(session.experiment, 'users'),
        'email': DeviceDataset(session.experiment, 'users')
    }


def ReactorSource(powerdev, name='FRM II'):
    """Return a typical reactor neutron source structure."""
    return {
        'name': ConstDataset(name, 'string'),
        'type': ConstDataset('Reactor Neutron Source', 'string'),
        'probe': ConstDataset('neutron', 'string'),
        'power': DeviceDataset(powerdev),
        # 'flux': ,
    }


def CounterMonitor(monitor):
    """Return a fission chamber monitor structure."""
    return {
        'mode': ConstDataset('monitor', 'string'),
        'type': ConstDataset('Fission_Chamber', 'string'),
        'preset': DeviceDataset(monitor, 'preselection', dtype='float',
                                units=counts),
        'integral': DetectorDataset(monitor, 'int', units=counts),
    }


def TimerMonitor(timer):
    """Return a timer monitor structure."""
    return {
        'mode': ConstDataset('timer', 'string'),
        'preset': DeviceDataset(timer, 'preselection', dtype='float',
                                units=seconds),
        'integral': DetectorDataset(timer, 'float', units=seconds),
    }


def Slit(device):
    """Return a slit structure."""
    return {
        'x_gap': DeviceDataset(f'{device}.width'),
        'y_gap': DeviceDataset(f'{device}.height'),
        'center:NXtransformations': {
            'x': DeviceDataset(f'{device}.centerx'),
            'y': DeviceDataset(f'{device}.centery'),
        },
    }


def Polarizer(typ='supermirror', **attrs):
    """Create a NXpolarizer structure.

    Optional keywords:

        reflection
        efficiency
        composition
    """
    ret = {'type': ConstDataset(typ, 'string')}
    if reflection := attrs.get('reflection'):
        ret['reflection'] = ConstDataset(reflection, 'float')
    if efficiency := attrs.get('efficiency'):
        ret['efficiency'] = ConstDataset(efficiency, 'float')
    if composition := attrs.get('composition'):
        ret['composition'] = ConstDataset(composition, 'string')
    return ret


def Flipper(typ='coil', **kwds):
    """Create a NXflipper structure.

    Optional keywords:
        -

    """
    return {
        'type': ConstDataset(typ, 'string'),
        # 'flip_turns':
        # 'comp_turns':
        # 'guide_turns':
        # 'flip_current':
        # 'comp_current':
        # 'thick_ness':
    }


def Selector(speed, wl, delta_wl, tilt):
    """Create a NXvelocity_selector structure."""
    return {
        'type': ConstDataset('Astrium Velocity Selector', 'string'),
        'rotation_speed': DeviceDataset(speed),
        # TODO: 'diameter' / 2
        'radius': DeviceDataset(delta_wl, 'diameter', dtype='float'),
        'spwidth': DeviceDataset(delta_wl, 'd_lamellae'),
        'length': DeviceDataset(wl, 'length'),
        'num': DeviceDataset(delta_wl, 'n_lamellae', dtype='int'),
        'twist': DeviceDataset(wl, 'twistangle'),
        'wavelength': DeviceDataset(wl, dtype='float'),
        'wavelength_spread': DeviceDataset(delta_wl, dtype='float'),
        'beamcenter': DeviceDataset(wl, 'beamcenter'),
        'tilt': DeviceDataset(tilt),
    }


def SollerCollimator(device, **args):
    """Create a NXcollimator structure for Soller type collimator.

    Optional keywords:
        - blade_thickness
        - blade_spacing
        - absorber

    """
    thickness = args.get('blade_thickness', 0.1)
    spacing = args.get('blade_spacing', 1)
    material = args.get('absorber', 'Gd')
    return {
        'type': ConstDataset('Soller', 'string'),
        'soller_angle': DeviceDataset(device, dtype='float'),
        'blade_thickness': ConstDataset(thickness, dtype='float', units=mm),
        'blade_spacing': ConstDataset(spacing, dtype='float', units=mm),
        'absorbing_material': ConstDataset(material, 'string'),
        'transmitting_material': ConstDataset('air', 'string'),
        'geometry:NXgeometry': {
            'shape:NXshape': {
                'shape': ConstDataset('nxbox', 'string'),
            },
        },
    }


def Filter(device, material, thickness=5):
    """Create a NXfilter structure."""
    density_map = {
        'C': 2.26,  # 2.25 - 2.265
        'Be': 1.848,
        'Al2O3': 4.0,  # 3.95 - 4.03
        'Si': 2.33,
        'Er': 9.045,
    }

    chem_formula_map = {
        'Beryllium': 'Be',
        'Pyrolytic Graphite': 'C',
        'Graphite': 'C',
        'Sapphire': 'Al2O3',
        'Silicon': 'Si',
        'Erbium': 'Er',
        'Supermirror': '',
    }

    chem_formula = chem_formula_map.get(material)
    density = density_map.get(chem_formula)
    return {
        'description': ConstDataset(material, 'string'),
        'status': DeviceDataset(device),
        # 'temperature_log:NXlog': ,
        'thickness': ConstDataset(thickness, dtype='float', units=mm),
        'chemical_formula': ConstDataset(chem_formula, dtype='string'),
        'density': ConstDataset(density, dtype='float', units=mass_density),
    }
