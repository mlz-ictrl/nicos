# -*- coding: utf-8 -*-

description = "Beam shutter setup"
group = "lowlevel"
display_order = 5

excludes = ['virtual_shutter']

tango_base = "tango://phys.kws1.frm2:10000/kws1/"

devices = dict(
    shutter_in  = device('devices.tango.DigitalInput',
                         tangodevice = tango_base + 'fzjdp_digital/shutter_in',
                         lowlevel = True,
                        ),
    shutter_set = device('devices.tango.DigitalOutput',
                         tangodevice = tango_base + 'fzjdp_digital/shutter_write',
                         lowlevel = True,
                        ),
    shutter     = device('kws1.shutter.Shutter',
                         description = 'shutter control',
                         output = 'shutter_set',
                         input = 'shutter_in',
                        ),
    nl3b_shutter = device('devices.taco.NamedDigitalInput',
                         description = 'Neutron guide 3b shutter status',
                         mapping = {'closed': 0, 'open': 1},
                         tacodevice = '//tacodb.taco.frm2/frm2/shutter/nl3b',
                         pollinterval = 60,
                         maxage = 120,
                        ),
    sixfold_shutter = device('devices.taco.NamedDigitalInput',
                         description = 'Sixfold shutter status',
                         mapping = {'closed': 0, 'open': 1},
                         tacodevice = '//tacodb.taco.frm2/frm2/shutter/sixfold',
                         pollinterval = 60,
                         maxage = 120,
                        ),
)
