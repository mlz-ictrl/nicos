#  -*- coding: utf-8 -*-

description = 'Slits/Pinholes'
group = 'optional'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    pinhole5 = device('devices.tango.NamedDigitalOutput',
        description = 'Pinhole 5mm radius',
        tangodevice = '%s/iobox/pinhole5' % tango_base,
        mapping = {'in': 1,
                   'out': 0},
    ),
    pinhole10 = device('devices.tango.NamedDigitalOutput',
        description = 'Pinhole 10mm radius',
        tangodevice = '%s/iobox/pinhole10' % tango_base,
        mapping = {'in': 1,
                   'out': 0},
    ),
    slit = device('devices.tango.NamedDigitalOutput',
        description = 'Slit 10x40mm',
        tangodevice = '%s/iobox/slit' % tango_base,
        mapping = {'in': 1,
                   'out': 0},
    ),
)
