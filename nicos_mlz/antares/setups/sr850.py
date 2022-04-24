description = 'Stanford SR-850 lock-in amplifier, for susceptibility measurements'
group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    sr850 = device('nicos_mlz.mira.devices.sr850.Amplifier',
        description = 'Stanford SR-850 lock-in amplifier, for susceptibility measurements',
        tangodevice = tango_base + 'network/sr830',
    ),
)

monitor_blocks = dict(
    default = Block('Lock-In',
        [
            BlockRow(
                Field(dev='sr850[0]', name='X'),
                Field(dev='sr850[1]', name='Y')
            ),
        ],
        setups='sr850',
    ),
)
