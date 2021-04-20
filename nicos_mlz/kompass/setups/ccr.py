description = 'CCR with LakeShore LS336 controller'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://kompasshw.kompass.frm2:10000/kompass/ls336'

devices = dict(
    # T_ccr = device('nicos_mlz.frm2.devices.ccr.CCRControl',
    #     description = 'The main temperature control device of the CCR',
    #     stick = 'T_ccr_stick',
    #     tube = 'T_ccr_tube',
    #     unit = 'K',
    #     fmtstr = '%.3f',
    # ),
    T_ccr_stick = device('nicos.devices.entangle.TemperatureController',
        description = 'The control device of the sample (stick)',
        tangodevice = '%s/control' % tango_base,
        abslimits = (0, 600),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    T_ccr_stick_range = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Heater range for the stick',
        tangodevice = '%s/range1' % tango_base,
        warnlimits = ('high', 'medium'),
        mapping = {'off': 0, 'low': 1, 'medium': 2, 'high': 3},
        unit = '',
    ),
    # T_ccr_tube = device('nicos.devices.entangle.TemperatureController',
    #     description = 'The control device of the tube',
    #     tangodevice = '%s/control2' % tango_base,
    #     abslimits = (0, 300),
    #     warnlimits = (0, 300),
    #     unit = 'K',
    #     fmtstr = '%.3f',
    # ),
    # T_ccr_tube_range = device('nicos.devices.entangle.NamedDigitalOutput',
    #     description = 'Heater range for the stick',
    #     tangodevice = '%s/range2' % tango_base,
    #     warnlimits = ('high', 'medium'),
    #     mapping = {'off': 0, 'low': 1, 'medium': 2, 'high': 3},
    #     unit = '',
    # ),
    T_ccr_ssample = device('nicos.devices.entangle.Sensor',
        description = '(optional) Sample temperature',
        tangodevice = '%s/sensb' % tango_base,
        unit = 'K',
        fmtstr = '%.3f',
    ),
    # T_ccr_sstick = device('nicos.devices.entangle.Sensor',
    #     description = '(regulation) Temperature at the stick',
    #     tangodevice = '%s/sensc' % tango_base,
    #     unit = 'K',
    #     fmtstr = '%.3f',
    # ),
    T_ccr_scoldhead = device('nicos.devices.entangle.Sensor',
        description = 'Temperature of the coldhead',
        tangodevice = '%s/sensa' % tango_base,
        warnlimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    # T_ccr_stube = device('nicos.devices.entangle.Sensor',
    #     description = '(regulation) Temperature at thermal coupling to the tube',
    #     tangodevice = '%s/sensd' % tango_base,
    #     warnlimits = (0, 300),
    #     unit = 'K',
    #     fmtstr = '%.3f',
    # ),
)

alias_config = {
    'T': {
        # 'T_ccr': 200,
        'T_ccr_stick': 150,
        # 'T_ccr_tube': 100
    },
    'Ts': {
        # 'T_ccr_sstick': 100,
        'T_ccr_ssample': 90,
        # 'T_ccr_stube': 20,
        'T_ccr_scoldhead': 10
    },
}

# startupcode = '''
# printinfo("===== ccr =====")
# printinfo("Please set T_ccr.regulationmode to either 'stick', 'tube', or 'both' "
#           "according to your needs.")
# printinfo("Activate the wanted channel with the ccr_pressure_regulate device or "
#           "switch it to 'off' to deactivate the regulation.")
# '''
