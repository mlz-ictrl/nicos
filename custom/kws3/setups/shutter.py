# -*- coding: utf-8 -*-

description = 'Shutter setup'
group = 'lowlevel'
display_order = 5

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'
tango_base_frm2 = 'tango://ictrlfs.ictrl.frm2:10000/frm2/'

excludes = ['virtual_shutter']

devices = dict(
    shutter         = device('nicos_mlz.jcns.devices.shutter.Shutter',
                             description = 'Experiment shutter',
                             tangodevice = tango_base + 'FZJDP_digital/ExpShutter',
                             mapping = {'closed': 2, 'open': 1},
                            ),
    nl3a_shutter    = device('nicos.devices.tango.NamedDigitalInput',
                             description = 'NL3a shutter status',
                             tangodevice = tango_base_frm2 + 'shutter/nl3a',
                             mapping = {'closed': 0, 'open': 1},
                            ),
    sixfold_shutter = device('nicos.devices.tango.NamedDigitalInput',
                             description = 'Sixfold shutter status',
                             tangodevice = tango_base_frm2 + 'shutter/sixfold',
                             mapping = {'closed': 0, 'open': 1},
                            ),
)
