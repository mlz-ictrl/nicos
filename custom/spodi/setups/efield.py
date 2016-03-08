description = 'Electric field sample stick'

group = 'optional'

includes = []

nethost = 'spodisrv.spodi.frm2'

devices = dict(
    e_field = device('devices.taco.AnalogOutput',
                     description = 'HV',
                     tacodevice = '//%s/spodi/hcp/hv' % nethost,
                     abslimits = (0, 10000),
                    ),
)

alias_config = {
}
