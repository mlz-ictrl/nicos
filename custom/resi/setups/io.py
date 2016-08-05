description = 'RESI IO controls'

group = 'optional'

devices = dict(
    prim_shutt=device('devices.taco.io.NamedDigitalOutput',
                      description='RESI prim. shutter',
                      tacodevice='//resictrl/resi/cpci15x/shutt_p',
                      maxage=1,
                      pollinterval=1,
                      mapping={'open': 1, 'closed': 0}
                      ),
    sec_shutt=device('devices.taco.io.NamedDigitalOutput',
                     description='RESI sec. shutter',
                     tacodevice='//resictrl/resi/cpci15x/shutt_s',
                     maxage=1,
                     pollinterval=1,
                     mapping={'open': 1, 'closed': 0}
                     ),
)
