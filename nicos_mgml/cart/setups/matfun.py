description = 'PPMS 14 Cryostat'

group = 'basic'

includes = ['alias_T', 'alias_B']

devices = dict(
    sn_matfun = device('nicos.devices.secop.SecNodeDevice',
        description='MATFUN SEC node',
        uri='kfes46.troja.mff.cuni.cz:5000',
        auto_create=True,
        # unit='',
        # count=0,
        # pollinterval=1,
    ),
    Gas14 = device('nicos.devices.generic.ManualMove',
        description = 'Gas Level',
        abslimits = (0, 1000000),
        default = 0,
        unit = '',
    ),
    matfun_cryostat = device('nicos_mgml.devices.cryostat.Cryostat',
        description = 'ppms9 cryostat',
        levelmeter = 'matfun_mgml_lev',
        gasmeter = 'Gas14',
        calibration = [(0, 1.5), (29, 4.36), (77.4, 34.5), (100, 36.2)],
        unit = '%',
    ),
)

alias_config = {
    'T': {'matfun_mgml_tt': 180},
    'Ts': {'matfun_mgml_tt': 60},
    'B': {'matfun_mgml_mf': 100},
    'Cryostat':  {'matfun_cryostat': 100},
}
