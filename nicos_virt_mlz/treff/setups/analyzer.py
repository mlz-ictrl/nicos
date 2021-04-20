description = 'Analyzer device'

group = 'optional'

devices = dict(
    analyzer_tilt = device('nicos.devices.generic.Axis',
        description = 'Analyzer tilt',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-0.81, 3.4),
            unit = 'deg',
        ),
        precision = 0.01,
        fmtstr = '%.3f',
    ),
    # aflipper = device('nicos_mlz.treff.devices.flipper.Flipper',
    #     description = 'Analyzer flip',
    #     flip = 'pow2flip',
    #     corr = 'pow2comp',
    #     currents = (1., 0.),
    # ),
    # pow2comp = device('nicos.devices.entangle.PowerSupply',
    #     description = 'Power supply 2 current control ch 1',
    #     tangodevice = tango_base + 'toellner/pow2comp',
    # ),
    # pow2flip = device('nicos.devices.entangle.PowerSupply',
    #     description = 'Power supply 2 current control ch 2',
    #     tangodevice = tango_base + 'toellner/pow2flip',
    # ),
    # pol_state = device("nicos.devices.generic.MultiSwitcher",
    #     description = "Guide field switcher",
    #     moveables = ["pflipper", "aflipper"],
    #     mapping = {
    #         "dd": ("down", "down"),
    #         "du": ("down", "up"),
    #         "ud": ("up", "down"),
    #         "uu": ("up", "up"),
    #     },
    #     precision = None,
    #     unit = ''
    # ),
)
