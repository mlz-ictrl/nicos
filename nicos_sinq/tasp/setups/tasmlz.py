description = 'This setup is for using the MLZ triple axis calculations'

group = 'basic'

includes = ['tasp']

sysconfig = dict(instrument = 'TASP',)

modules = ['nicos.commands.tas', ]

devices = dict(
    TASP = device('nicos_sinq.devices.tassinq.SinqTAS',
        description = 'TASP in MLZ mode',
        instrument = 'TASP',
        responsible = 'Alexandra Turrini <alexandra.turrini@psi.ch>',
        cell = 'Sample',
        phi = 'a4',
        psi = 'a3',
        mono = 'mono',
        ana = 'ana',
        alpha = None,
        psi360 = False,
        scatteringsense = (-1, 1, -1),
        energytransferunit = 'meV',
        axiscoupling = False,
    ),
    h = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the h of hkl',
        alias = 'TASP.h',
        devclass = 'nicos.devices.tas.spectro.TASIndex'
    ),
    k = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the k of hkl',
        alias = 'TASP.k',
        devclass = 'nicos.devices.tas.spectro.TASIndex'
    ),
    l = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the l of hkl',
        alias = 'TASP.l',
        devclass = 'nicos.devices.tas.spectro.TASIndex'
    ),
    en = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the transferred energy',
        alias = 'TASP.E',
        devclass = 'nicos.devices.tas.spectro.TASIndex'
    ),
)
