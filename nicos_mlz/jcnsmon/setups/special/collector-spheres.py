description = 'setup for the NICOS collector service'
group = 'special'

devices = dict(
    SECache = device('nicos.services.collector.MappingCacheForwarder',
        cache = 'localhost',
        prefix = 'nicos/se',
        keyfilters = ['.*cct6.*', '.*ccm8v.*', '.*h_.*', '.*v_.*',
                      '.*setpoint.*', '.*c_.*', '.*t_.*'],
        map = {
            'h_sample': 'cct21_h_sample',
            'h_tube': 'cct21_h_tube',
            't_sample': 'cct21_t_sample',
            't_tube': 'cct21_t_tube',
            'v_flood': 'cct21_v_flood',
            'v_vacuum': 'cct21_v_vacuum',
            'setpoint': 'cct21_setpoint',
            'c_temperature': 'cct21_c_temperature',
            'c_pressure': 'cct21_c_pressure',
        }
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'phys.spheres.frm2',
        forwarders = ['SECache'],
    ),
)
