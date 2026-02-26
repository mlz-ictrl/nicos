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
#   Mark Koennecke <mark.koennecke@psi.ch>
#   Artur Glavic <artur.glavic@psi.ch>
#
# *****************************************************************************

from copy import deepcopy
import numpy as np

from nicos import session
from nicos.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceAttribute, DeviceDataset, NamedImageDataset, NexusElementBase, NXAttribute, NXLink, \
    NXScanLink, StartTime, EndTime
from nicos.nexus.nexussink import NexusTemplateProvider

from nicos_sinq.nexus.specialelements import SaveSampleEnv

class DetectorAxesCalculator(NexusElementBase):
    """Placeholder for calculating axes geometry parameters for an NXdata group.

    Uses a set of devices to find detector position in space. Uses pixel sizes
    to calculate angular pixel positions. Uses wavelength device to calculate q.
    """

    def __init__(self, distance_device,
                 x_shape=128, y_shape=128,
                 x_size=1000., y_size=1000.,
                 x_device=None, y_device=None,
                 x_offset=0., y_offset=0.,
                 x_flip=False, y_flip=False,
                 wl_device=None,
                 **attr):
        NexusElementBase.__init__(self)
        self.distance_device = distance_device
        self.wl_device = wl_device
        self.x_shape = x_shape
        self.y_shape = y_shape
        self.x_size = x_size
        self.y_size = y_size
        self.x_device = x_device
        self.y_device = y_device
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.x_flip = x_flip
        self.y_flip = y_flip

        self.attrs = {}
        for key, val in attr.items():
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
            self.attrs[key] = val

    def get_device_value(self, device, sinkhandler):
        if (device, 'value') in sinkhandler.dataset.metainfo:
            return sinkhandler.dataset.metainfo[(device, 'value')][0]
        try:
            dev = session.getDevice(self.device)
            return dev.read()
        except Exception:
            return 0.

    def create(self, name, h5parent, sinkhandler):
        x = np.linspace(0.5, -0.5, self.x_shape) * self.x_size + self.x_offset
        y = np.linspace(-0.5, 0.5, self.y_shape) * self.y_size + self.y_offset
        L = self.get_device_value(self.distance_device, sinkhandler)

        if self.x_flip:
            x = -x+2*self.x_offset
        if self.y_flip:
            y = -y+2*self.y_offset

        if self.x_device is not None:
            xpos = self.get_device_value(self.x_device, sinkhandler)
            x+=xpos
        if self.y_device is not None:
            ypos = self.get_device_value(self.y_device, sinkhandler)
            y+=ypos

        dset = h5parent.create_dataset('posx', (self.x_shape,), dtype=float)
        dset[:] = x
        dset.attrs['units'] = 'mm'
        dset.attrs['long_name'] = 'Horizontal Distance to Beam (X) / mm'
        dset = h5parent.create_dataset('posy', (self.y_shape,), dtype=float)
        dset[:] = y
        dset.attrs['units'] = 'mm'
        dset.attrs['long_name'] = 'Vertical Distance to Beam (Y) / mm'

        dset = h5parent.create_dataset('tthx', (self.x_shape,), dtype=float)
        dset[:] = np.arctan2(x, L)*(180/np.pi)
        dset.attrs['units'] = 'degrees'
        dset.attrs['long_name'] = 'Horizontal Scattering Angle / °'
        dset = h5parent.create_dataset('tthy', (self.y_shape,), dtype=float)
        dset[:] = np.arctan2(y, L)*(180/np.pi)
        dset.attrs['units'] = 'degrees'
        dset.attrs['long_name'] = 'Vertical Scattering Angle / °'

        if self.wl_device is not None:
            wl = self.get_device_value(self.wl_device, sinkhandler)
            dset = h5parent.create_dataset('Qx', (self.x_shape,), dtype=float)
            dset[:] = np.sin(np.arctan2(x, L)/2.)*4.*np.pi/wl
            dset.attrs['units'] = '1/nm'
            dset.attrs['long_name'] = 'Horizontal Scattering Vector / (1/nm)'
            dset = h5parent.create_dataset('Qy', (self.y_shape,), dtype=float)
            dset[:] = np.sin(np.arctan2(y, L)/2.)*4.*np.pi/wl
            dset.attrs['units'] = '1/nm'
            dset.attrs['long_name'] = 'Vertical Scattering Vector / (1/nm)'

        #self.createAttributes(dset, sinkhandler)

DET_CONFIG = {
    'sa_xmin': 27,
    'sa_xmax': 154,
    'wa_xmin': 23,
    'wa_xmax': 158,
    }
DET_CONFIG['sa_xpix'] = DET_CONFIG['sa_xmax']-DET_CONFIG['sa_xmin']+1
DET_CONFIG['wa_xpix'] = DET_CONFIG['wa_xmax']-DET_CONFIG['wa_xmin']+1

sansllb_default = {
    'default': NXAttribute('entry0', 'string'),
    'NeXus_Version': NXAttribute('4.4.0', 'string'),
    'instrument': NXAttribute('SANS-LLB at SINQ', 'string'),
    'owner': DeviceAttribute('SANS-LLB', 'responsible'),
    'entry0:NXentry': {
        'default': NXAttribute('central_data', 'string'),
        'title': DeviceDataset('Exp', 'title'),
        'proposal_title': DeviceDataset('Exp', 'title'),
        'proposal_id': DeviceDataset('Exp', 'proposal'),
        'start_time': StartTime(), 'end_time': EndTime(),
        'definition': ConstDataset('NXsas', 'string'),
        'user:NXuser': {
            'name': DeviceDataset('Exp', 'users'),
            'email': DeviceDataset('Exp', 'localcontact')
        },
        'proposal_user:NXuser': {
            'name': DeviceDataset('Exp', 'users'),
        },
        'control:NXmonitor': {
            'preset': DetectorDataset('preset', 'float32'),
            'mode': DetectorDataset('mode', 'string'),
            'count_time': DetectorDataset('elapsedtime', 'float32'),
            'integral': DetectorDataset('monitor1', 'int32',
                                        units=NXAttribute('counts',
                                                          'string')),
        },
        'monitor2:NXmonitor': {
            'integral': DetectorDataset('monitor2', 'int32', units='counts'),
        },
        'monitor1:NXmonitor': {
            'integral': DetectorDataset('monitor1', 'int32', units='counts'),
        },
        'monitor0:NXmonitor': {
            'integral': DetectorDataset('monitor0', 'int32', units='counts'),
        },
        'protoncount:NXmonitor': {
            'integral': DetectorDataset('protoncount', 'int32', units='counts'),
        },
        'central_data:NXdata': {
            'data': NXLink('/entry0/SANS-LLB/central_detector/data'),
            'signal': NXAttribute('data', 'string'),
            'axes': NXAttribute(['tthy', 'tthx'], 'S30'),
            'x': ConstDataset(np.arange(DET_CONFIG['sa_xpix']).tolist(),
                              dtype='float', long_name='Horizontal Direction X', units='pixel'),
            'y': ConstDataset(np.arange(128).tolist(), dtype='float', long_name='Vertical Direction Y', units='pixel'),
            'none': DetectorAxesCalculator('dtlz', DET_CONFIG['sa_xpix'], 128,
                                           5.0*DET_CONFIG['sa_xpix'], 640.,
                                           wl_device='wavelength', x_device='dtlx')
            },
        'left_data:NXdata': {
            'data': NXLink('/entry0/SANS-LLB/left_detector/data'),
            'signal': NXAttribute('data', 'string'),
            'axes':   NXAttribute(['tthy', 'tthx'], 'S30'),
            'x':      ConstDataset(np.arange(16).tolist(), dtype='float', long_name='Horizontal Direction X',
                                   units='pixel'),
            'y':      ConstDataset(np.arange(DET_CONFIG['wa_xpix']).tolist(), dtype='float', long_name='Vertical Direction Y',
                                   units='pixel'),
            'none':   DetectorAxesCalculator('dthz', 16, DET_CONFIG['wa_xpix'],
                                             # apparent640 size is bigger due to pixels without signal
                                             214.4, 5.0*DET_CONFIG['wa_xpix'], y_flip=True,
                                             wl_device='wavelength', x_device='dthx', y_device='dthy',
                                             x_offset=246.55, y_offset=-50) # x: bd-x_offset+341.25-214.4/2
            },
        'bottom_data:NXdata': {
             'data': NXLink('/entry0/SANS-LLB/bottom_detector/data'),
            'signal': NXAttribute('data', 'string'),
            'axes':   NXAttribute(['tthy', 'tthx'], 'S30'),
            'x':      ConstDataset(np.arange(DET_CONFIG['wa_xpix']).tolist(), dtype='float', long_name='Horizontal Direction X',
                                   units='pixel'),
            'y':      ConstDataset(np.arange(16).tolist(), dtype='float', long_name='Vertical Direction Y',
                                   units='pixel'),
            'none':   DetectorAxesCalculator('dthz', DET_CONFIG['wa_xpix'], 16,
                                             # apparent size is bigger due to pixels without signal
                                             5.0*DET_CONFIG['wa_xpix'], 214.4,
                                             wl_device='wavelength', x_device='dthx', y_device='dthy',
                                             x_offset=12.5, y_offset=-468.0), # y: ld-y_offset−214.4/2−324.65 adjust +13.85
            },
    }
}  # root

inst_default = {
    'name': ConstDataset('SANS-LLB', 'string'),
    'attenuator:NXattenuator': {
        'selection': DeviceDataset('att'),
    },
    'beam_stop:NXbeam_stop': {
        'x': DeviceDataset('bsx', dtype='float'),
        'y': DeviceDataset('bsy', dtype='float'),
        'size': ConstDataset(70.0, 'float', units='mm'), # TODO: make this depend on BS selection
        'inclination': ConstDataset(35, 'float', units='degree'),
    },
    'collimator:NXcollimator': {
        'geometry:NXgeometry': {
            'shape': ConstDataset('nxbox', 'string'),
            'size':  DeviceDataset('coll', dtype='float', units='mm'),
            },
        'length': NXLink('/entry0/SANS-LLB/collimator/geometry/size'),
    },
    #'polariser:NXpolariser': {
    #    'selection': DeviceDataset('pol'),
    #    'position': DeviceDataset('polpos'),
    #},
    'SINQ:NXsource': {
        'name': ConstDataset('SINQ, Paul Scherrer Institute', 'string'),
        'type': ConstDataset('Spallation Neutron Source', 'string'),
        'probe': ConstDataset('neutron', 'string'),
        'target_material': ConstDataset('Pb', 'string'),
    },
    'velocity_selector:NXvelocity_selector': {
        'type': ConstDataset('Dornier Velocity Selector',
                             'string'),
        'wavelength': DeviceDataset('wavelength'),
        'wavelength_spread': DeviceDataset('wavelength', parameter='fwhm'),
        'rotation_speed': DeviceDataset('velocity_selector'),
        'twist': ConstDataset(0, float,
                              units=NXAttribute('degree', 'string')),
    },
}

central_detector = {
    'layout' : ConstDataset('area', 'string'),
    'x': DeviceDataset('dtlx'),
    'x_set': DeviceDataset('dtlx', parameter='target'),
    'x_offset': DeviceDataset('dtlx', parameter='offset'),
    'distance': DeviceDataset('detz'),
    'z': DeviceDataset('dtlz'),
    'z_set': DeviceDataset('dtlz', parameter='target'),
    'z_offset': DeviceDataset('dtlz', parameter='offset'),
    'data': NamedImageDataset('det_main'),
    'raw_data': NamedImageDataset('det_image'),
    # 640mm square detector with 512x128 pixels
    'x_pixel_size': ConstDataset(5.0, float,
                                 units=NXAttribute('mm', 'string')),
    'y_pixel_size': ConstDataset(5.0, float,
                                 units=NXAttribute('mm', 'string')),
    'beam_center_x': ConstDataset(61.5, float,
                                  units=NXAttribute('pixel', 'string')),
    'beam_center_y': ConstDataset(DET_CONFIG['sa_xpix']/2.+0.5, float,
                                  units=NXAttribute('pixel', 'string')),
    'type': ConstDataset('monoblock', 'string'),
    'deadtime': ConstDataset(3.5E-6, 'float'),
}

left_detector = {
    'layout' : ConstDataset('area', 'string'),
    'x': DeviceDataset('dthx'),
    'x_set': DeviceDataset('dthx', parameter='target'),
    'x_offset': DeviceDataset('dthx', parameter='offset'),
    'y': DeviceDataset('dthy'),
    'y_set': DeviceDataset('dthy', parameter='target'),
    'y_offset': DeviceDataset('dthy', parameter='offset'),
    'distance': DeviceDataset('dthz'),
    'distance_set': DeviceDataset('dthz', parameter='target'),
    'z_offset': DeviceDataset('dthz', parameter='offset'),
    'data': NamedImageDataset('det_side'),
    # 'raw_data': SliceImage('high_q_raw', 256,  0, 16),
    'x_pixel_size': ConstDataset(13.4, float,
                                 units=NXAttribute('mm', 'string')),
    'y_pixel_size': ConstDataset(5.0, float,
                                 units=NXAttribute('mm', 'string')),
    'type': ConstDataset('3He tubes', 'string'),
    'deadtime': ConstDataset(3.5E-6, 'float'),
}


bottom_detector = {
    'layout' : ConstDataset('area', 'string'),
    'x': DeviceDataset('dthx'),
    'x_set': DeviceDataset('dthx', parameter='target'),
    'x_offset': DeviceDataset('dthx', parameter='offset'),
    'y': DeviceDataset('dthy'),
    'y_set': DeviceDataset('dthy', parameter='target'),
    'y_offset': DeviceDataset('dthy', parameter='offset'),
    'distance': DeviceDataset('dthz'),
    'distance_set': DeviceDataset('dthz', parameter='target'),
    'z_offset': DeviceDataset('dthz', parameter='offset'),
    'data': NamedImageDataset('det_lower'),
    'x_pixel_size': ConstDataset(5.0, float,
                                 units=NXAttribute('mm', 'string')),
    'y_pixel_size': ConstDataset(13.4, float,
                                 units=NXAttribute('mm', 'string')),
    'type': ConstDataset('3He tubes', 'string'),
    'deadtime': ConstDataset(3.5E-6, 'float'),
}

sample_common = {
    'name': DeviceDataset('Sample', 'samplename'),
    'x': DeviceDataset('stx'),
    'x_set': DeviceDataset('stx', parameter='target'),
    'y': DeviceDataset('sty'),
    'y_set': DeviceDataset('sty', parameter='target'),
    'z': DeviceDataset('stz'),
    'z_set': DeviceDataset('stz', parameter='target'),
    'omega': DeviceDataset('stom'),
    'sgu': DeviceDataset('stgn'),
    'lieselotte': SaveSampleEnv(),
}


class SANSLLBTemplateProvider(NexusTemplateProvider):
    def makeGuide(self, no):
        result = {
            'selection': DeviceDataset('col%d' % no),
            'position': DeviceDataset('col%dpos' % no),
            'position_set': DeviceDataset('col%dpos' % no,
                                          parameter='target'),
            'm_value': ConstDataset(3, float),
        }
        return result

    def makeSlit(self, no):
        result = {
            'x_gap': DeviceDataset('slit%d.width' % no, defaultval=0),
            'y_gap': DeviceDataset('slit%d.height' % no, defaultval=0),
            'motors:NXcollection': {
                'left':       DeviceDataset('sl%dxp'%no, defaultval=0),
                'right':      DeviceDataset('sl%dxn'%no, defaultval=0),
                'bottom':     DeviceDataset('sl%dyp'%no, defaultval=0),
                'top':        DeviceDataset('sl%dyn'%no, defaultval=0),
                'left_set':   DeviceDataset('sl%dxp'%no, parameter='target', defaultval=0),
                'right_set':  DeviceDataset('sl%dxn'%no, parameter='target', defaultval=0),
                'bottom_set': DeviceDataset('sl%dyp'%no, parameter='target', defaultval=0),
                'top_set':    DeviceDataset('sl%dyn'%no, parameter='target', defaultval=0),
                'x_center': DeviceDataset('slit%d.centerx'%no, defaultval=0),
                'y_center': DeviceDataset('slit%d.centery'%no, defaultval=0),
                },
        }
        return result

    def makeInstrument(self):
        result = deepcopy(inst_default)
        coll = result['collimator:NXcollimator']
        # VLB: start from 1, since the guide 0 is now called pol
        for i in range(0, 6):
            coll['guide%d:NXguide' % i] = self.makeGuide(i)
            coll['slit%d:NXslit' % i] = self.makeSlit(i)
        coll['slit6:NXslit'] = self.makeSlit(6)
        coll['slit6:NXslit']['distance'] = DeviceDataset('sl6_distance', defaultval=1500.)
        result['central_detector:NXdetector'] = deepcopy(central_detector)
        result['left_detector:NXdetector'] = deepcopy(left_detector)
        result['bottom_detector:NXdetector'] = deepcopy(bottom_detector)
        # Integrated counts also as scan dataset
        counters = ['roi1', 'roi2', 'det_main', 'det_lower', 'det_side']
        # TODO: the x-key is overwritten by ScanLink device name, should be fixed.
        result['integral_counts:NXdata'] = {
                'x': NXScanLink(),
                'axes':   NXAttribute(['x'], 'S30'),
                'signal': NXAttribute('data', 'string'),
                'auxiliary_signals':   NXAttribute(counters, 'S30'),
                'data': DetectorDataset('det_image', dtype=int),
                }
        for ctr in counters:
            result['integral_counts:NXdata'][ctr] = DetectorDataset(ctr, dtype=int)
        return result

    def getTemplate(self):
        full = deepcopy(sansllb_default)
        entry = full['entry0:NXentry']
        entry['SANS-LLB:NXinstrument'] = self.makeInstrument()
        entry['sample:NXsample'] = deepcopy(sample_common)
        return full
