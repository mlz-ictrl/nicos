# -*- coding: utf-8 -*-

description = 'DNS monochromator and polarizer'

group = 'lowlevel'

tango_host = 'tango://phys.dns.frm2:10000'
tango_mot = tango_host + '/dns/fzjs7/'

devices = dict(

    pol_trans    = device('devices.tango.Motor',
                          description = 'Polarizer translation',
                          tangodevice = tango_mot + 'pol_trans',
                         ),
    pol_rot      = device('devices.tango.Motor',
                          description = 'Polarizer rotation',
                          tangodevice = tango_mot + 'pol_rot',
                         ),
)
