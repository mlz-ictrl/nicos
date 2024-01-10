description = 'Sample lift for 1T electromagnet'

display_order = 52

group = 'lowlevel'

pvprefix = 'SQ:AMOR:mmac1:'
magprefix = 'SQ:AMOR:magnet:'

excludes = ['stz_table', 'smz_table']

devices = dict(
    smz = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Sample lift with magnet installed',
        motorpv = pvprefix + 'smz',
        errormsgpv = pvprefix + 'smz-MsgTxt',
        can_disable = True,
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    fma = device('nicos_sinq.tasp.devices.slsmagnet.SLSMagnet',
        description = 'fat sample magnet',
        readpv = magprefix + 'fma:CurRBV',
        writepv = magprefix + 'fma:CurSet',
        wenable = magprefix + 'fma:STATUS',
        renable = magprefix + 'fma:STATUS_RBV',
        precision = .1,
        abslimits = (-100., 100.)
    ),
)
alias_config = {'sz': {'smz': 10}}
