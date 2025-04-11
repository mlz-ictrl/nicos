description = 'Monochromator devices'

group = 'optional'

tango_base = 'tango://motorbox03.erwin.frm2.tum.de:10000/box/'

devices = dict(
    mtz = device('nicos.devices.entangle.Motor',
        description = 'z translation motor of monochromator system',
        tangodevice = tango_base + 'channel1/motor',
        # visibility = (),
    ),
    mom = device('nicos.devices.entangle.Motor',
        description = 'omega motor of monochromator system',
        tangodevice = tango_base + 'channel2/motor',
        # visibility = (),
    ),

# XXX: attocubes?

# multiswitcher for mono selection
    mono_select = device('nicos.devices.generic.MultiSwitcher',
        description = 'Mono changer',
        moveables = ['mom', 'mtz'],
        mapping = {
            'Cu': [-45, 2],  # XXX: correct values after neutron checks
            'Ge': [-43, 90],
        },
        fallback = None,
        fmtstr = '%s',
        precision = [0.05, 0.05],
        blockingmove = True,
    ),
)
