#  -*- coding: utf-8 -*-

description = 'Attenuators'
group = 'optional'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda/iobox'

devices = dict(
    att0 = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Attenuator 0: factor 3',
        tangodevice = '%s/plc_att_0' % tango_base,
        mapping = {'in': 1,
                   'out': 0},
    ),
    att1 = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Attenuator 1: factor 15',
        tangodevice = '%s/plc_att_1' % tango_base,
        mapping = {'in': 1,
                   'out': 0},
    ),
    att2 = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Attenuator 2: factor 30',
        tangodevice = '%s/plc_att_2' % tango_base,
        mapping = {'in': 1,
                   'out': 0},
    ),
)
