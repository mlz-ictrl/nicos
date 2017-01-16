description = 'Stanford SR-850 lock-in amplifier, for susceptibility measurements'
group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    sr850 = device('mira.sr850.Amplifier',
        description = 'Stanford SR-850 lock-in amplifier, for susceptibility measurements',
        tangodevice = tango_base + 'network/sr830',
    ),
)
