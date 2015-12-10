# -*- coding: utf-8 -*-

description = 'lens switching devices'
group = 'lowlevel'

includes = ['collimation']

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'

devices = dict(
    lens_set  = device('devices.tango.DigitalOutput',
                       tangodevice = tango_base + 'fzjdp_digital/lens_write',
                       lowlevel = True,
                      ),
    lens_in   = device('devices.tango.DigitalInput',
                       tangodevice = tango_base + 'fzjdp_digital/lens_in',
                       lowlevel = True,
                      ),
    lens_out  = device('devices.tango.DigitalInput',
                       tangodevice = tango_base + 'fzjdp_digital/lens_out',
                       lowlevel = True,
                      ),
    lenses    = device('kws1.lens.Lenses',
                       description = 'high-level lenses device',
                       output = 'lens_set',
                       input_in = 'lens_in',
                       input_out = 'lens_out',
                       sync_bit = 'coll_sync',
                      ),
)
