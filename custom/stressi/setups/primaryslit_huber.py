description = 'Primary slit Huber automatic'

group = 'optional'

excludes = ['primaryslit_manual']

servername = 'VME'

nameservice = 'stressictrl.stressi.frm2'

devices = dict(
    psw = device('devices.vendor.caress.Motor',
                 description = 'HWB PSW',
                 fmtstr = '%.2f',
                 unit = 'mm',
                 coderoffset = -2049.02,
                 abslimits = (0, 7),
                 nameserver = '%s' % (nameservice,),
                 objname = '%s' % (servername),
                 config = 'PSW 114 11 0x00f1c000 4 4096 1000 100 2 24 50 0 0 1'
                          ' 3000 1 10 0 0 0',
                 ),
    psh = device('devices.vendor.caress.Motor',
                 description = 'HWB PSH',
                 fmtstr = '%.2f',
                 unit = 'mm',
                 coderoffset = 0,
                 abslimits = (0, 17),
                 nameserver = '%s' % (nameservice,),
                 objname = '%s' % (servername),
                 config = 'PSH 115 11 0x00f1d000 2 100 100 10 1 0 0 0 0 1 '
                          '3000 1 10 0 0 0',
                 ),
)

startupcode = '''
# psh.userlimits = psh.abslimits
# psw.userlimits = psw.abslimits
'''
