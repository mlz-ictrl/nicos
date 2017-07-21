# -*- coding: utf-8 -*-

description = "Beam shutter setup"
group = "lowlevel"
display_order = 5

excludes = ['virtual_shutter']

tango_base = "tango://phys.kws2.frm2:10000/kws2/"

devices = dict(
    shutter_in  = device('nicos.devices.tango.DigitalInput',
                         tangodevice = tango_base + 'fzjdp_digital/shutter_in',
                         lowlevel = True,
                        ),
    shutter_set = device('nicos.devices.tango.DigitalOutput',
                         tangodevice = tango_base + 'fzjdp_digital/shutter_write',
                         lowlevel = True,
                        ),
    shutter     = device('nicos_mlz.kws1.devices.shutter.Shutter',
                         description = 'shutter control',
                         output = 'shutter_set',
                         input = 'shutter_in',
                         timeout = 300,
                        ),
    nl3a_shutter = device('nicos.devices.taco.NamedDigitalInput',
                         description = 'NL3a shutter status',
                         mapping = {'closed': 0, 'open': 1},
                         tacodevice = '//tacodb.taco.frm2/frm2/shutter/nl3a',
                        ),
    sixfold_shutter = device('nicos.devices.taco.NamedDigitalInput',
                         description = 'Sixfold shutter status',
                         mapping = {'closed': 0, 'open': 1},
                         tacodevice = '//tacodb.taco.frm2/frm2/shutter/sixfold',
                        ),
)
