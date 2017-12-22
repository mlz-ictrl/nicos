description = 'CCR with LakeShore LS336 controller'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    T_ccr = device('nicos_mlz.frm2.devices.ccr.CCRControl',
        description = 'The main temperature control device of the CCR',
        stick = 'T_ccr_stick',
        tube = 'T_ccr_tube',
        unit = 'K',
        fmtstr = '%.3f',
    ),
    T_ccr_stick = device('nicos.devices.tango.TemperatureController',
        description = 'The control device of the sample (stick)',
        tangodevice = '%s/ccr/ctrl_stick' % tango_base,
        abslimits = (0, 600),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    T_ccr_tube = device('nicos.devices.tango.TemperatureController',
        description = 'The control device of the tube',
        tangodevice = '%s/ccr/ctrl_tube' % tango_base,
        abslimits = (0, 300),
        warnlimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    T_ccr_ssample = device('nicos.devices.tango.Sensor',
        description = '(optional) Sample temperature',
        tangodevice = '%s/ccr/sens_sample' % tango_base,
        unit = 'K',
        fmtstr = '%.3f',
    ),
    T_ccr_sstick = device('nicos.devices.tango.Sensor',
        description = '(regulation) Temperature at the stick',
        tangodevice = '%s/ccr/sens_stick' % tango_base,
        unit = 'K',
        fmtstr = '%.3f',
    ),
    T_ccr_scoldhead = device('nicos.devices.tango.Sensor',
        description = 'Temperature of the coldhead',
        tangodevice = '%s/ccr/sens_coldhead' % tango_base,
        warnlimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
    ),
    T_ccr_stube = device('nicos.devices.tango.Sensor',
        description = '(regulation) Temperature at thermal coupling to the tube',
        tangodevice = '%s/ccr/sens_tube' % tango_base,
        warnlimits = (0, 300),
        unit = 'K',
        fmtstr = '%.3f',
    ),
)

alias_config = {
    'T': {
        'T_ccr': 200,
        'T_ccr_stick': 150,
        'T_ccr_tube': 100
    },
    'Ts': {
        'T_ccr_sstick': 100,
        'T_ccr_ssample': 90,
        'T_ccr_stube': 20,
        'T_ccr_scoldhead': 10
    },
}

startupcode = '''
printinfo("===== ccr =====")
printinfo("Please set T_ccr.regulationmode to either 'stick', 'tube', or 'both' "
          "according to your needs.")
printinfo("Activate the wanted channel with the ccr_pressure_regulate device or "
          "switch it to 'off' to deactivate the regulation.")
'''
