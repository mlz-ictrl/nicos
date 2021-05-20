description = 'Devices for the Pfeiffer vakuum measuring device'

pvprefix = 'SQ:FOCUS:PFIFF:'

devices = dict(
    pf_flightpath = device('nicos.devices.epics.EpicsReadable',
        description = 'Vakuum value for flightpath',
        epicstimeout = 3.0,
        readpv = pvprefix + 'Flightpath',
        lowlevel = True
    ),
    pf_antitrumpet = device('nicos.devices.epics.EpicsReadable',
        description = 'Vakuum value for antitrumpet',
        epicstimeout = 3.0,
        readpv = pvprefix + 'Antitrumpet',
        lowlevel = True
    ),
    pf_sample = device('nicos.devices.epics.EpicsReadable',
        description = 'Vakuum value for sample chamber',
        epicstimeout = 3.0,
        readpv = pvprefix + 'SampleChamber',
        lowlevel = True
    ),
    pf_bef = device('nicos.devices.epics.EpicsReadable',
        description = 'Vakuum value for BE filter',
        epicstimeout = 3.0,
        readpv = pvprefix + 'BeFilter',
        lowlevel = True
    ),
    pfeiffer = device('nicos_sinq.focus.devices.pfeiffer.PfeifferReadable',
        description = 'Master device for pfeiffer',
        sensors = ['pf_flightpath', 'pf_antitrumpet', 'pf_sample', 'pf_bef'],
        switchstates = {
            'enable': 1,
            'disable': 0
        },
        switchpvs = {
            'read': pvprefix + 'SWITCH_RBV',
            'write': pvprefix + 'SWITCH'
        },
        unit = 'mbar'
    ),
)
