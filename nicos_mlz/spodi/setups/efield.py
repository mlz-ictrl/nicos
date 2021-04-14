description = 'Electric field sample stick'

group = 'optional'

tango_base = 'tango://spodisrv.spodi.frm2:10000/spodi/hcp/'

devices = dict(
    E = device('nicos.devices.tango.PowerSupply',
        description = 'Sample environment: electrical field',
        tangodevice = tango_base + 'hv',
        abslimits = (0, 35000),
        unit = 'V',
    ),
    E_c = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'HV current',
        device = 'E',
        parameter = 'current',
        unit = 'A',
        fmtstr = '%g',
    ),
)
