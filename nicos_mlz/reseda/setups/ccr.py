description = 'CCR with LakeShore LS336 controller'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    #T_ccr = device('nicos_mlz.devices.ccr.CCRControl',
    #    description = 'The main temperature control device of the CCR',
    #    stick = 'T_ccr_stick',
    #    tube = 'T_ccr_tube',
    #    unit = 'K',
    #    fmtstr = '%.3f',
    #),
    T_ccr_stick = device('nicos.devices.tango.TemperatureController',
        description = 'The control device of the sample (stick)',
        tangodevice = '%s/ccr/control2' % tango_base,
        abslimits = (0, 350),
        unit = 'K',
        fmtstr = '%.2f',
        pollinterval = 10,
        maxage = 19,
    ),
    T_ccr_tube = device('nicos.devices.tango.TemperatureController',
        description = 'The control device of the tube',
        tangodevice = '%s/ccr/control' % tango_base,
        abslimits = (0, 320),
        warnlimits = (0, 320),
        unit = 'K',
        fmtstr = '%.2f',
        pollinterval = 10,
        maxage = 19,
    ),
    T_ccr_sample_stick_a = device('nicos.devices.tango.Sensor',
        description = '(optional) Sample temperature',
        tangodevice = '%s/ccr/sensa' % tango_base,
        unit = 'K',
        fmtstr = '%.2f',
        pollinterval = 10,
        maxage = 19,
    ),
    T_ccr_sample_stick_b = device('nicos.devices.tango.Sensor',
        description = '(regulation) Temperature at the stick',
        tangodevice = '%s/ccr/sensb' % tango_base,
        unit = 'K',
        fmtstr = '%.2f',
        pollinterval = 10,
        maxage = 19,
    ),
    T_ccr_cold_head = device('nicos.devices.tango.Sensor',
        description = 'Temperature of the coldhead',
        tangodevice = '%s/ccr/sensc' % tango_base,
        warnlimits = (0, 350),
        unit = 'K',
        fmtstr = '%.2f',
        pollinterval = 10,
        maxage = 19,
    ),
    T_ccr_sample_tube = device('nicos.devices.tango.Sensor',
        description = '(regulation) Temperature at thermal coupling to the tube',
        tangodevice = '%s/ccr/sensd' % tango_base,
        warnlimits = (0, 350),
        unit = 'K',
        fmtstr = '%.2f',
        pollinterval = 10,
        maxage = 19,
    ),
    P_ccr = device('nicos.devices.tango.Sensor',
        description = 'Pressure in the neutron guide elements',
        tangodevice = '%s/ccr/p1' % tango_base,
        fmtstr = '%.1f',
        unit = 'mbar'
    ),
)

alias_config = {
    'T': {
        #'T_ccr': 200,
        'T_ccr_stick': 150,
        'T_ccr_tube': 100
    },
    'Ts': {
        'T_ccr_stick': 100,
        #'T_ccr_ssample': 90,
        'T_ccr_tube': 20,
        #'T_ccr_scoldhead': 10
    },
}

