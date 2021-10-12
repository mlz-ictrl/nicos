description = 'Installs the Eulerian cradle into NICOS'

includes = ['orion']

excludes = ['euler', 'oriontas']

devices = dict(
    ORION = device('nicos_sinq.orion.devices.orion.OrionSXTal',
        description = 'instrument object',
        instrument = 'SINQ ORION',
        responsible = 'Oksana Zaharko <oksana.zaharko@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/orion/',
        ttheta = 'stt',
        omega = 'som',
        chi = 'chi',
        phi = 'phi',
        mono = 'mono',
        center_counter = 'gausscount',
        center_steps = [.1, .1, .2, .2]
    ),
    h = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the h of hkl',
        alias = 'ORION.h',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    k = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the k of hkl',
        alias = 'ORION.k',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    l = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the l of hkl',
        alias = 'ORION.l',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
)
