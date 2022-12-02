group = 'basic'

description = 'Lakeshore devices'

tango_base = 'tango://localhost:10000/box/ls/'

devices = dict(
    det = device('nicos.devices.generic.Detector',
        description = 'collection of measurement devices',
        others = ['R'],
    ),
    R = device('nicos_jcns.resist.devices.measure.MeasureChannel',
        description = 'resistance measurement',
        tangodevice = tango_base + 'chan_d',
        unit = 'Ohm',
    ),
    T = device('nicos.devices.entangle.TemperatureController',
        description = 'control channel temperature',
        tangodevice = tango_base + 'control_b',
        unit = 'K',
    ),
    Tset = device('nicos.devices.generic.ParamDevice',
        description = 'setpoint of control channel',
        device = 'T',
        parameter = 'setpoint',
        unit = 'K',
    ),
    Trange = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'heater range of control channel',
        tangodevice = tango_base + 'heater_b',
        unit = '',
        mapping = dict(off=0, low=1, med=2, high=3),
    ),
    Ts = device('nicos.devices.entangle.Sensor',
        description = 'sample temperature sensor',
        tangodevice = tango_base + 'chan_c',
        unit = 'K',
    ),
    Tc = device('nicos.devices.entangle.Sensor',
        description = 'cryostat temperature sensor',
        tangodevice = tango_base + 'chan_a',
        unit = 'K',
    ),
)
