description = 'motors that are avalible by default'

group = 'optional'

tangobase = 'tango://localhost:10000/test/'

devices = dict(
    sample_Rz_m_sim = device('nicos.devices.entangle.Motor',
        description = 'Rz-axis motor',
        tangodevice = tangobase + 'sim/motor',
        visibility = (),
    ),
    sample_Rz = device('nicos.devices.generic.Axis',
        description = 'Rz-axis motor',
        motor = 'sample_Rz_m_sim',
        precision = 0.001,
    ),
)
