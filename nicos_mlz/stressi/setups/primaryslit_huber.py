description = 'Primary slit Huber automatic'

group = 'optional'

excludes = ['primaryslit_manual']

tango_base = 'tango://motorbox03.stressi.frm2.tum.de:10000/box/'

devices = dict(
    psw_m = device('nicos.devices.tango.Motor',
        tangodevice = tango_base + 'channel3/motor',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    psw_c = device('nicos.devices.tango.Sensor',
        tangodevice = tango_base + 'channel3/coder',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    psw = device('nicos.devices.generic.Axis',
        description = 'Primary slit width, horizontal opening (PSW)',
        motor = 'psw_m',
        coder = 'psw_c',
        precision = 0.01,
    ),
    psh_m = device('nicos.devices.tango.Motor',
        fmtstr = '%.2f',
        tangodevice = tango_base + 'channel4/motor',
        lowlevel = True,
    ),
    psh_c = device('nicos.devices.tango.Sensor',
        tangodevice = tango_base + 'channel4/coder',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    psh = device('nicos.devices.generic.Axis',
        description = 'Primary slit height, vertical opening (PSH)',
        motor = 'psh_m',
        coder = 'psh_c',
        precision = 0.01,
    ),
)

startupcode = '''
# psh.userlimits = psh.abslimits
# psw.userlimits = psw.abslimits
'''
