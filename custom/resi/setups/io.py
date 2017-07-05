description = 'RESI IO controls'

group = 'optional'

devices = dict(
    prim_shutt = device('nicos.devices.taco.io.NamedDigitalOutput',
        description = 'RESI prim. shutter',
        tacodevice = '//resictrl/resi/cpci15x/shutt_p',
        maxage = 1,
        pollinterval = 1,
        mapping = {'open': 1,
                   'closed': 0}
    ),
    sec_shutt = device('nicos.devices.taco.io.NamedDigitalOutput',
        description = 'RESI sec. shutter',
        tacodevice = '//resictrl/resi/cpci15x/shutt_s',
        maxage = 1,
        pollinterval = 1,
        mapping = {'open': 1,
                   'closed': 0}
    ),
    hover_mono = device('nicos.devices.taco.io.NamedDigitalOutput',
        description = 'RESI hover feet (opt.bench + gonio base)',
        tacodevice = '//resictrl/resi/cpci15x/press_g',
        maxage = 1,
        pollinterval = 1,
        mapping = {'on': 1,
                   'off': 0}
    ),
    hover_theta = device('nicos.devices.taco.io.NamedDigitalOutput',
        description = 'RESI hover feet (detector)',
        tacodevice = '//resictrl/resi/cpci15x/press_t',
        maxage = 1,
        pollinterval = 1,
        mapping = {'on': 1,
                   'off': 0}
    ),
)
