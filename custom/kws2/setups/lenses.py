# -*- coding: utf-8 -*-

description = 'lens switching devices'
group = 'lowlevel'
display_order = 75

excludes = ['virtual_lenses']

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    lenses    = device('kws1.lens.Lenses',
                       description = 'high-level lenses device',
                       io = 'lens_io',
                      ),

    lens_set  = device('devices.tango.DigitalOutput',
                       tangodevice = tango_base + 'fzjdp_digital/lens_write',
                       fmtstr = '%#x',
                       lowlevel = True,
                      ),
    lens_in   = device('devices.tango.DigitalInput',
                       tangodevice = tango_base + 'fzjdp_digital/lens_in',
                       fmtstr = '%#x',
                       lowlevel = True,
                      ),
    lens_out  = device('devices.tango.DigitalInput',
                       tangodevice = tango_base + 'fzjdp_digital/lens_out',
                       fmtstr = '%#x',
                       lowlevel = True,
                      ),
    lens_sync = device('devices.tango.DigitalOutput',
                       tangodevice = tango_base + 'fzjdp_digital/sync_bit',
                       fmtstr = '%#x',
                       lowlevel = True,
                      ),
    lens_io   = device('kws1.lens.LensControl',
                       description = 'lens I/O device',
                       output = 'lens_set',
                       input_in = 'lens_in',
                       input_out = 'lens_out',
                       sync_bit = 'lens_sync',
                       timeout = 30.0,
                       lowlevel = True,
                      ),
)
