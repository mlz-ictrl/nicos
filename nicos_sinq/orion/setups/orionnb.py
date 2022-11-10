description = 'Installs normal beam geometry into ORION. This is for testing purposes' \
              'only, ORION does not do normal beam'

includes = ['orion']
excludes = ['eulerorion', 'euler', 'oriontas']

devices = dict(
    ORION = device('nicos_sinq.sxtal.instrument.LiftingSXTal',
        description = 'instrument object',
        instrument = 'SINQ ORION',
        responsible = 'Oksana Zaharko <oksana.zaharko@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/orion/',
        gamma = 'stt',
        omega = 'som',
        nu = 'sgl',
        mono = 'mono',
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
