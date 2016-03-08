# -*- coding: utf-8 -*-

description = 'ANTARES switchable sockets'

group = 'optional'

tango_base = 'tango://slow.antares.frm2:10000/antares/'

devices = dict()

for n in range(1, 16):  # from 01 to 15
    devices['socket%02d' % n] = \
        device('devices.tango.NamedDigitalOutput',
               description = 'Powersocket %02d' % n,
               tangodevice = tango_base + 'fzjdp_digital/Socket%02d' % n,
               mapping = dict(on=1, off=0),
              )
