description = 'Example Sans2D Pixel Detector Setup with Instrument View'

group = 'basic'

sysconfig = dict(
    instrument = 'sans2d',
)

devices = dict(
    sans2d = device('nicos_demo.mantid.devices.instrument.ViewableInstrument',
        description = 'instrument object',
        responsible = 'R. Esponsible <r.esponsible@stfc.ac.uk>',
        instrument = 'sans2d',
        website = 'http://www.nicos-controls.org',
        operators = ['ISIS developer team'],
        facility = 'ISIS demo instruments',
        idf = 'SANS2D_Definition.xml'
    ),
    sample = device('nicos_mlz.sans1.devices.sans1_sample.Sans1Sample',
        description = 'sample object',
    ),
    mot_z = device('nicos.devices.generic.VirtualMotor',
        description = 'front detector position in the tube',
        abslimits = (19.281, 23.281),
        curvalue = 23.281,
        precision = 3,
        speed = 1,
        unit = 'm',
        fmtstr = '%.3f',
    ),
    mot_x = device('nicos.devices.generic.VirtualMotor',
        description = 'horizontal offset of detector',
        abslimits = (1.0, 5.0),
        speed = 0.5,
        unit = 'm',
        curvalue = 1.1,
    ),
    mot_omega = device('nicos.devices.generic.VirtualMotor',
        description = 'tilt of detector',
        abslimits = (-40, 40),
        speed = 1.5,
        unit = 'deg',
        curvalue = 0,
        fmtstr = '%.1f',
    ),
    mantid_move_det = device('nicos_demo.mantid.devices.devices.MantidTranslationDevice',
        args = {'RelativePosition': False,
                'ComponentName': 'front-detector'},
        x = 'mot_x',
        z = 'mot_z',
        lowlevel = True,
    ),
    mantid_rot_det = device('nicos_demo.mantid.devices.devices.MantidRotationDevice',
        args = {'RelativeRotation': False,
                'ComponentName': 'front-detector'},
        y = 1,
        angle = 'mot_omega',
        lowlevel = True,
    ),
)

startupcode = '''
printinfo("============================================================")
printinfo("Welcome to the Sans 2D Instrument View demo setup.")
printinfo("============================================================")
'''
