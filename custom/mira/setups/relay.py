description = 'polarity reversing relays'
group = 'optional'

devices = dict(
    relay1    = device('mira.beckhoff.NamedDigitalOutput',
                       description = 'polarity switchover relay 1',
                       tangodevice = 'tango://mira1.mira.frm2:10000/mira/beckhoff/beckhoff1',
                       startoffset = 0,
                       mapping = {'off': 0, 'on': 1},
                      ),
    relay2    = device('mira.beckhoff.NamedDigitalOutput',
                       description = 'polarity switchover relay 2',
                       startoffset = 1,
                       tangodevice = 'tango://mira1.mira.frm2:10000/mira/beckhoff/beckhoff1',
                       mapping = {'off': 0, 'on': 1},
                      ),
)
