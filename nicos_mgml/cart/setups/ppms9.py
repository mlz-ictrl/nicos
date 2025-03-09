description = 'PPMS 9 Cryostat'

group = 'basic'

includes = ['alias_T', 'alias_B']

devices = dict(
    secnode = device('nicos.devices.secop.SecNodeDevice',
        description='PPMS9 SEC node',
        uri='kfes38.troja.mff.cuni.cz:5000',
        auto_create=True,
        # unit='',
        # count=0,
        # pollinterval=1,
    ),
    Gas9 = device('nicos.devices.generic.ManualMove',
        description = 'Gas Level',
        abslimits = (0, 1000000),
        default = 0,
        unit = '',
    ),
    ppms9_cryostat = device('nicos_mgml.devices.cryostat.Cryostat',
        description = 'ppms9 cryostat',
        levelmeter = 'ppms9_mgml_lev',
        gasmeter = 'Gas9',
        calibration = [(0, 1.5), (29, 4.36), (77.4, 34.5), (100, 36.2)],
        unit = '%',
    ),
)

extended = {
    'autodevices': ['ppms9_mgml_tt', 'ppms9_mgml_mf'],
}

alias_config = {
    'T': {'ppms9_mgml_tt': 180},
    'Ts': {'ppms9_mgml_tt': 60},
    'B': {'ppms9_mgml_mf': 100},
    'Cryostat':  {'ppms9_cryostat': 100},
}
