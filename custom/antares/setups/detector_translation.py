description = 'Detector Table Experimental Chamber 1'

group = 'optional'

tango_host = 'tango://cpci01.antares.frm2:10000'

devices = dict(
    dtx = device('devices.tango.Motor',
                 description = 'Detector Translation X',
                 tangodevice = '%s/antares/fzjs7/X_det' % tango_host,
                 abslimits = (0, 580),
                 userlimits = (0, 580),
                ),
    dty = device('devices.tango.Motor',
                 description = 'Detector Translation Y',
                 tangodevice = '%s/antares/fzjs7/Y_det' % tango_host,
                 abslimits = (0, 300),
                 userlimits = (0, 300),
                ),
)

startupcode = '''
'''
