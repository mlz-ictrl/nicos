description = 'Sample lift for 1T electromagnet'

display_order = 53

pvprefix = 'SQ:AMOR:mmac1:'

excludes = ['stz_table', 'SampleMagnet']

devices = dict(
    smz = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Sample lift with magnet installed',
        motorpv = pvprefix + 'smz',
        errormsgpv = pvprefix + 'smz-MsgTxt',
        can_disable = True,
        auto_enable = False,
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
)
alias_config = {'sz': {'smz': 100}}
