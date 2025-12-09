description = 'External ILL camera'

group = 'optional'

devices = dict(
    trigger_hw = device('nicos.devices.generic.ManualSwitch',
        states = [0, 1],
        visibility = (),
    ),
    trigger = device('nicos.devices.generic.Pulse',
        description = 'Camera trigger',
        onvalue = 1,
        offvalue = 0,
        ontime = 0.1,
        moveable = 'trigger_hw',
    ),
    timer_ill = device('nicos_mlz.antares.devices.TriggerTimer',
        description = 'Software timer sending trigger signal',
        trigger = 'trigger',
    ),
    det_ill = device('nicos.devices.generic.Detector',
        description = 'The ILL detector',
        timers = ['timer_ill'],
    ),
)

