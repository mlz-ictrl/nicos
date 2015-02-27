description = 'HUBER Sample Table Experimental Chamber 1'

group = 'optional'

tango_host = 'tango://cpci01.antares.frm2:10000'

devices = dict(
    stx_huber = device('devices.tango.Motor',
                       description = 'Sample Translation X',
                       tangodevice = '%s/antares/fzjs7/Probe_X' % tango_host,
                       abslimits = (0, 400),
                      ),
    sty_huber = device('devices.tango.Motor',
                       description = 'Sample Translation Y',
                       tangodevice = '%s/antares/fzjs7/Probe_Y' % tango_host,
                       abslimits = (0, 400),
                      ),
    sgx       = device('devices.tango.Motor',
                       description = 'Sample Rotation around X',
                       tangodevice = '%s/antares/fzjs7/Probe_tilt_x' % tango_host,
                       abslimits = (-10, 10),
                      ),
    sgz       = device('devices.tango.Motor',
                       description = 'Sample Rotation around Z',
                       tangodevice = '%s/antares/fzjs7/Probe_tilt_z' % tango_host,
                       abslimits = (-10, 10),
                      ),
    sry_huber = device('devices.tango.Motor',
                       description = 'Sample Rotation around Y',
                       tangodevice = '%s/antares/fzjs7/Probe_phi' % tango_host,
                       abslimits = (-999999, 999999),
                      ),
)

startupcode = '''
'''
