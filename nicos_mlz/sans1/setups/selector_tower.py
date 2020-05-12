description = 'Selector Tower Movement'

group = 'lowlevel'

nethost = 'sans1srv.sans1.frm2'

tango_base = 'tango://sans1hw.sans1.frm2:10000/sans1/'

devices = dict(
    selector_ng_ax = device('nicos.devices.generic.Axis',
        description = 'selector neutron guide axis',
        motor = 'selector_ng_mot',
        coder = 'selector_ng_enc',
        precision = 0.1,
        fmtstr = '%.2f',
        #refpos = -141.75,
        maxage = 120,
        pollinterval = 15,
        lowlevel = True,
        requires = dict(level='admin'),
    ),
    selector_ng_mot = device('nicos.devices.tango.Motor',
        description = 'selector neutron guide motor',
        tangodevice = tango_base + 'selector/z_mot',
        fmtstr = '%.2f',
        #abslimits = (-140, 140), old
        abslimits = (-140, 142.5), #new
        userlimits = (-140, 142.5), #new
        lowlevel = True,
        requires = dict(level='admin'),
    ),
    selector_ng_enc = device('nicos.devices.tango.Sensor',
        description = 'selector neutron guide encoder',
        tangodevice = tango_base + 'selector/z_enc',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    selector_ng = device('nicos.devices.generic.Switcher',
        description = 'selector neutron guide switcher',
        # lowlevel = True,
        moveable = 'selector_ng_ax',
        # mapping = {'sel1': -140, 'ng': 0, 'sel2': 140}, old value
        # mapping = {'SEL1': -138.4, 'NG': 1.6, 'SEL2': 141.6}, #new "tisane"-value
        # mapping = {'SEL1': -137.6, 'NG': 2.4, 'SEL2': 142.4}, #new "tisane"-value
        mapping = {'SEL1 NVS042': -137.6, 'NG': 2.4, 'SEL2 NVS020': 142.4}, #new "tisane"-value
        precision = 0.01,
        requires = dict(level='admin'),
    ),
    selector_tilt = device('nicos.devices.generic.Axis',
        description = 'selector tilt axis',
        motor = 'selector_tilt_mot',
        coder = 'selector_tilt_enc',
        precision = 0.05,
        fmtstr = '%.2f',
        abslimits = (-7.5, 7.5),
        maxage = 120,
        pollinterval = 15,
        offset = 0,
        requires = dict(level='admin'),
    ),
    selector_tilt_mot = device('nicos.devices.tango.Motor',
        description = 'selector tilt motor',
        tangodevice = tango_base + 'selector/tilt_mot',
        fmtstr = '%.2f',
        abslimits = (-10, 10),
        lowlevel = True,
        requires = dict(level='admin'),
    ),
    selector_tilt_enc = device('nicos.devices.tango.Sensor',
        description = 'selector tilt encoder',
        tangodevice = tango_base + 'selector/tilt_enc',
        fmtstr = '%.2f',
        lowlevel = True,
    ),

)
