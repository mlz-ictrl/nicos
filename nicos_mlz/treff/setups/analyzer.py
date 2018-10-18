description = 'Analyzer device'

group = 'optional'

tango_base = 'tango://phys.treff.frm2:10000/treff/'

devices = dict(
    analyzer_tilt = device('nicos.devices.tango.Motor',
        description = 'Analyzer tilt',
        tangodevice = tango_base + 'FZJS7/analyzer_tilt',
        precision = 0.01,
        fmtstr = '%.3f',
        unit = 'deg',
    ),
    aflipper = device('nicos_mlz.treff.devices.flipper.Flipper',
        description = 'Analyzer flip',
        flip = 'pow2flip',
        corr = 'pow2comp',
        currents = (1., 0.),
    ),
    pow2comp = device('nicos.devices.tango.PowerSupply',
        description = 'Power supply 2 current control ch 1',
        tangodevice = tango_base + 'toellner/pow2comp',
    ),
    pow2flip = device('nicos.devices.tango.PowerSupply',
        description = 'Power supply 2 current control ch 2',
        tangodevice = tango_base + 'toellner/pow2flip',
    ),
    pol_state = device("nicos.devices.generic.MultiSwitcher",
        description = "Guide field switcher",
        moveables = ["pflipper", "aflipper"],
        mapping = {
            "dd": ("down", "down"),
            "du": ("down", "up"),
            "ud": ("up", "down"),
            "uu": ("up", "up"),
        },
        precision = None,
        unit = ''
    ),
)
