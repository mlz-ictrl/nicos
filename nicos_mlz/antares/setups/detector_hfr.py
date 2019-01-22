description = 'H(igh) F(rame) R(ate) detector setup'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

includes = ['shutters']

devices = dict(
    det_hfr = device('nicos_mlz.antares.devices.detector.AndorHFRCamera',
        description = 'Andor Basic HFR',
        tangodevice = tango_base + 'andor/io',
        fastshutter = 'fastshutter',
        spooldirectory = 'E:\\spool\\',
    ),
)

startupcode = """
SetDetectors(det_hfr)
"""
