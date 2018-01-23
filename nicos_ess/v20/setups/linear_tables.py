description = 'Setup with two permanently available linear tables via CARESS.'

servername = 'EXV20'
nameservice = '192.168.1.254'

devices = dict(
    lin1 = device('nicos.devices.vendor.caress.Motor',
        description = 'Huber linear table 400 mm',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = 0,
        abslimits = (0, 400),
        loglevel = 'debug',
        nameserver = '%s' % (nameservice,),
        objname = '%s' % (servername),
        config = 'LIN1 500 nist222dh1787.hmi.de:/st222.caress_object '
                 'CopleyStepnet 17 2000 CopleyStepnet 17 2000 0',
        loadblock = '''start=never,async
stop=never,async
read=always,async
motion_TBG=0.1
motion_TBK=0.01
motion_usefloat=true
motion_autodelete=false
motion_display=36
motion_displayformat=%0.3f
motion_retries=1
loadoffset=yes
'''
    ),
    lin2 = device('nicos.devices.vendor.caress.Motor',
        description = 'Huber linear table 100mm',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = 0,
        abslimits = (0, 100),
        nameserver = '%s' % (nameservice,),
        objname = '%s' % (servername),
        config = 'LIN2 500 nist222dh1787.hmi.de:/st222.caress_object '
                 'CopleyStepnet 18 4000 CopleyStepnet 18 4000 0',
        loadblock = '''start=never,async
stop=never,async
read=always,async
motion_TBG=0.1
motion_TBK=0.01
motion_usefloat=true
motion_autodelete=false
motion_display=36
motion_displayformat=%0.3f
motion_retries=1
loadoffset=yes
'''
    ),
)
