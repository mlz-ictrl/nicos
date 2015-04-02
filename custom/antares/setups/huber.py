description = 'HUBER Sample Table Experimental Chamber 1'

group = 'optional'

tango_host = 'tango://cpci01.antares.frm2:10000'

devices = dict(
    stx_huber = device('devices.tango.Motor',
                       description = 'Sample Translation X',
                       tangodevice = '%s/antares/fzjs7/Probe_X' % tango_host,
                       precision = 0.01,
                       abslimits = (0, 400),
                       pollinterval = 5,
                       maxage = 12,
                      ),
    sty_huber = device('devices.tango.Motor',
                       description = 'Sample Translation Y',
                       tangodevice = '%s/antares/fzjs7/Probe_Y' % tango_host,
                       precision = 0.01,
                       abslimits = (0, 400),
                       pollinterval = 5,
                       maxage = 12,
                      ),
    sgx_huber       = device('devices.tango.Motor',
                       description = 'Sample Rotation around X',
                       tangodevice = '%s/antares/fzjs7/Probe_tilt_x' % tango_host,
                       precision = 0.01,
                       abslimits = (-10, 10),
                       pollinterval = 5,
                       maxage = 12,
                      ),
    sgz_huber       = device('devices.tango.Motor',
                       description = 'Sample Rotation around Z',
                       tangodevice = '%s/antares/fzjs7/Probe_tilt_z' % tango_host,
                       precision = 0.01,
                       abslimits = (-10, 10),
                       pollinterval = 5,
                       maxage = 12,
                      ),
    sry_huber = device('devices.tango.Motor',
                       description = 'Sample Rotation around Y',
                       tangodevice = '%s/antares/fzjs7/Probe_phi' % tango_host,
                       precision = 0.01,
                       abslimits = (-999999, 999999),
                       pollinterval = 5,
                       maxage = 12,
                      ),
)

startupcode = '''
'''
