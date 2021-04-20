description = 'JASCO Fourier-transforming infrared spectrometer'

group = 'optional'

tango_base = 'tango://phys.kws2.frm2:10000/box/'

devices = dict(
    ftir_pol_rot = device('nicos.devices.entangle.Motor',
        description = 'Polarizer angle',
        tangodevice = tango_base + 'pol/pos',
        unit = 'deg',
        fmtstr = '%.0f',
        precision = 1.0,
    ),
    ftir_pol_tbl = device('nicos.devices.entangle.Motor',
        description = 'Polarizer translation stage',
        tangodevice = tango_base + 'table/pos',
        unit = 'mm',
        fmtstr = '%.1f',
        precision = 0.1,
    ),
    ftir_sample_tbl = device('nicos.devices.entangle.Motor',
        description = 'Sample translation stage',
        tangodevice = tango_base + 'table2/pos',
        unit = 'mm',
        fmtstr = '%.1f',
        precision = 0.1,
    ),
    FTIR = device('nicos_mlz.kws2.devices.ftir.FTIRSpectro',
        description = 'FTIR spectrometer',
        trigger_out = device('nicos.devices.entangle.DigitalOutput',
            tangodevice = tango_base + 'lj/trigger',
        ),
        status_in = device('nicos.devices.entangle.DigitalInput',
            tangodevice = tango_base + 'lj/status',
        ),
        fileno_in = device('nicos.devices.entangle.DigitalInput',
            tangodevice = tango_base + 'spectro/fileno',
        ),
        polarizer = 'ftir_pol_rot'
    ),
)
