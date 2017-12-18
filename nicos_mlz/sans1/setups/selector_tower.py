description = 'Selector Tower Movement'

group = 'lowlevel'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    # selector_speed = device('nicos.devices.taco.Axis',
    #     tacodevice = '//%s/sans1/table/z-2a' % (nethost, ),
    #     fmtstr = '%.2f',
    #     abslimits = (-10, 10),
    # ),
    selector_ng_ax = device('nicos.devices.generic.Axis',
        description = 'selector neutron guide axis',
        motor = 'selector_ng_mot',
        coder = 'selector_ng_enc',
        obs = [],
        precision = 0.1,
        fmtstr = '%.2f',
        #refpos = -141.75,
        #abslimits = (-140, 140), alt
        abslimits = (-140, 142.5), #new
        userlimits = (-140, 142.5), #new
        maxage = 120,
        pollinterval = 15,
        lowlevel = True,
    ),
    selector_ng_mot = device('nicos.devices.taco.motor.Motor',
        description = 'selector neutron guide motor',
        tacodevice = '//%s/sel/z/motor' % (nethost, ),
        fmtstr = '%.2f',
        #abslimits = (-140, 140), old
        abslimits = (-140, 142.5), #new
        userlimits = (-140, 142.5), #new
        lowlevel = True,
    ),
    selector_ng_enc = device('nicos.devices.taco.coder.Coder',
        description = 'selector neutron guide encoder',
        tacodevice = '//%s/sel/z/enc' % (nethost, ),
        fmtstr = '%.2f',
        lowlevel = True,
    ),

    selector_ng = device('nicos.devices.generic.Switcher',
        description = 'selector neutron guide switcher',
        #lowlevel = True,
        moveable = 'selector_ng_ax',
        #mapping = {'sel1': -140, 'ng': 0, 'sel2': 140}, old value
        #mapping = {'SEL1': -138.4, 'NG': 1.6, 'SEL2': 141.6}, #new "tisane"-value
        mapping = {'SEL1': -137.6, 'NG': 2.4, 'SEL2': 142.4}, #new "tisane"-value
        precision = 0.01,
    ),

    selector_tilt = device('nicos.devices.generic.Axis',
        description = 'selector tilt axis',
        motor = 'selector_tilt_mot',
        coder = 'selector_tilt_enc',
        obs = [],
        precision = 0.05,
        fmtstr = '%.2f',
        #refpos = -11.17,
        abslimits = (-7.5+2.27, 7.5+2.27),
        userlimits = (-7.5, 7.5),
        maxage = 120,
        pollinterval = 15,
        #offset = 1, old
        #offset = 1.72, #new
        offset = 2.27, #new
    ),
    selector_tilt_mot = device('nicos.devices.taco.motor.Motor',
        description = 'selector tilt motor',
        tacodevice = '//%s/sel/tilt/motor' % (nethost, ),
        fmtstr = '%.2f',
        abslimits = (-10, 10),
        lowlevel = True,
    ),
    selector_tilt_enc = device('nicos.devices.taco.coder.Coder',
        description = 'selector tilt encoder',
        tacodevice = '//%s/sel/tilt/enc' % (nethost, ),
        fmtstr = '%.2f',
        lowlevel = True,
    ),

)
