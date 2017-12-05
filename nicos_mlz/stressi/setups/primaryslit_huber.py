description = 'Primary slit Huber automatic'

group = 'optional'

excludes = ['primaryslit_manual']

servername = 'VME'

nameservice = 'stressictrl.stressi.frm2'

devices = dict(
    psw = device('nicos.devices.vendor.caress.EKFMotor',
                 description = 'HWB PSW',
                 fmtstr = '%.2f',
                 unit = 'mm',
                 coderoffset = -245.12,
                 abslimits = (0, 7),
                 nameserver = '%s' % (nameservice,),
                 objname = '%s' % (servername),
                 config = 'PSW 114 11 0x00f1c000 4 4096 1000 100 2 24 50 -1 0 '
                          '1 3000 1 10 0 0 0',
                ),
    psh = device('nicos.devices.vendor.caress.EKFMotor',
                 description = 'HWB PSH',
                 fmtstr = '%.2f',
                 unit = 'mm',
                 coderoffset = -232.31,
                 abslimits = (0, 17),
                 nameserver = '%s' % (nameservice,),
                 objname = '%s' % (servername),
                 config = 'PSH 114 11 0x00f1d000 2 4096 1000 100 2 24 50 -1 0 '
                          '1 3000 1 10 0 0 0',
                ),
)

startupcode = '''
# psh.userlimits = psh.abslimits
# psw.userlimits = psw.abslimits
'''
