description = 'Mouse button devices'
group = 'optional'

tango_base = 'tango://motorpi:10000/tomo/digital/'

devices = dict(
    mouse_button = device('nicos.devices.entangle.DigitalOutput',
        description = 'Mouse button',
        tangodevice = tango_base + 'mousebutton',
        visibility = (),
        fmtstr = '%d',
    ),
    mouse = device('nicos.devices.generic.Pulse',
        description = 'Mouse button click device',
        moveable = 'mouse_button',
        onvalue = 1,
        offvalue = 0,
        ontime = 0.1,
    ),
)
