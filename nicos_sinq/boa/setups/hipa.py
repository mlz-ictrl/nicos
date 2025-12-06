description = 'HIPA Current'

group = 'lowlevel'

devices = dict(
    hipa_current = device(
        'nicos.devices.epics.pva.epics_devices.EpicsReadable',
        description = "Proton Current",
        readpv = "SQ:BOA:proton:BEAM",
        monitor = True,
        visibility = {'devlist'},
    ),
)

extended = dict(
    representative = 'hipa_current',
)
