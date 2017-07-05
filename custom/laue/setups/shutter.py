description = 'Display RESI shutter status'
group = 'optional'

devices = dict(
    primarydown = device('nicos.devices.taco.DigitalInput',
        description = 'RESI primary shutter state:closed',
        tacodevice = '//resi1.resi.frm2/resi/cpci15x/shutt_pd'
    ),
    primaryup = device('nicos.devices.taco.DigitalInput',
        description = 'RESI primary shutter state:open',
        tacodevice = '//resi1.resi.frm2/resi/cpci15x/shutt_pu'
    )
)
