description = 'PGAA detectors'

group = 'lowlevel'

includes = []

sysconfig = dict(
    datasinks = ['sink']
)

nethost = 'pgaasrv.pgaa.frm2'

devices = dict(
    det = device('nicos_mlz.pgaa.devices.dspec.DSPec',
        description = '60%',
        tangodevice = 'tango://silver.pgaa.frm2:10000/PGAA/MCA/60',
        prefix = 'P',
        maxage = None
    ),
    detLEGe = device('nicos_mlz.pgaa.devices.dspec.DSPec',
        description = 'low energy germanium detector',
        tangodevice = 'tango://silver.pgaa.frm2:10000/PGAA/MCA/LEGe',
        prefix = 'L',
        maxage = None
    ),
    # _60p = device('nicos_mlz.pgaa.devices.dspec.DSPec',
    #     description = '60%',
    #     tangodevice = 'tango://silver.pgaa.frm2:10000/PGAA/MCA/60',
    #     prefix = 'P',
    #     maxage = None,
    # ),
    # LEGe = device('nicos_mlz.pgaa.devices.dspec.DSPec',
    #     description = 'low energy germanium detector',
    #     tangodevice = 'tango://silver.pgaa.frm2:10000/PGAA/MCA/LEGe',
    #     prefix = 'L',
    #     maxage = None,
    # ),
)
