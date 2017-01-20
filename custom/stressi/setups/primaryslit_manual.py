description = 'Primary slit manual adjustment'

group = 'optional'

excludes = ['primaryslit_huber']

devices = dict(
    psw = device('devices.generic.ManualMove',
                 description = 'Slit Width',
                 fmtstr = '%.2f',
                 default = 1,
                 unit = 'mm',
                 abslimits = (0, 30),
                 requires =  {'level': 'admin',},
                ),

    psh = device('devices.generic.ManualMove',
                 description = 'Slit Height',
                 fmtstr = '%.2f',
                 default = 1,
                 unit = 'mm',
                 abslimits = (0, 30),
                 requires =  {'level': 'admin',},
                ),

)

startupcode = '''
# psh.userlimits = psh.abslimits
# psw.userlimits = psw.abslimits
'''
