description = 'Detector Table Experimental Chamber 1'

group = 'optional'

tango_base = 'tango://slow.antares.frm2:10000/antares/'

devices = dict(
    dtx = device('devices.tango.Motor',
                 description = 'Detector Translation X',
                 tangodevice = tango_base + 'fzjs7/X_det',
                 abslimits = (0, 580),
                 userlimits = (0, 580),
                ),
    dty = device('devices.tango.Motor',
                 description = 'Detector Translation Y',
                 tangodevice = tango_base + 'fzjs7/Y_det',
                 abslimits = (0, 300),
                 userlimits = (0, 300),
                ),
)

startupcode = '''
'''
