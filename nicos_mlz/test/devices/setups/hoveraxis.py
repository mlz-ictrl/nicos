includes = ['axis']

devices = dict(
    airpad = device('nicos.devices.generic.ManualSwitch',
        states = (0, 1),
    ),
    hoveraxis = device('nicos_mlz.devices.axes.HoveringAxis',
        motor = 'motor',
        coder = 'coder',
        switch = 'airpad',
        startdelay = 2.0,
        stopdelay = 2.0,
        fmtstr = '%.2f',
        precision = 0.05,
        unit = 'deg',
    ),
)
