description = 'Electric field sample stick'

group = 'optional'

includes = []

nethost = 'spodisrv.spodi.frm2'

devices = dict(
    E = device('devices.taco.VoltageSupply',
               description = 'HV',
               tacodevice = '//%s/spodi/hcp/hv' % nethost,
               abslimits = (0, 10000),
               unit = 'V',
              ),
    E_c = device('devices.taco.AnalogInput',
                 description = 'HV current',
                 tacodevice = '//%s/spodi/hcp/current' % nethost,
                 unit = 'A',
                 fmtstr = '%g',
                ),
)

alias_config = {
}
