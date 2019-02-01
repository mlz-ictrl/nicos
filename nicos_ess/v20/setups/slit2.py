description = 'Slit 2'
servername = 'EXV20'
nameservice = '192.168.1.254'

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

devices = dict(
    slit2hl = device('nicos.devices.vendor.caress.Motor',
        description = 'Slit 2 Horizontal Left',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = 0,
        abslimits = (-30, 30),
        nameserver = '%s' % (nameservice,),
        objname = '%s' % (servername),
        config = 'MB2HL 500 nist222dh1787.hmi.de:/st222.caress_object '
                 'CopleyStepnet 8 -4000 BeckhoffKL5001 BK5120/63/32/24/0 '
                 '-4096 223135',
        lowlevel = True,
        loadblock = loadblock
    ),
    slit2hr = device('nicos.devices.vendor.caress.Motor',
        description = 'Slit 2 Horizontal Right',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = 0,
        abslimits = (-30, 30),
        nameserver = '%s' % (nameservice,),
        objname = '%s' % (servername),
        config = 'MB2HR 500 nist222dh1787.hmi.de:/st222.caress_object '
                 'CopleyStepnet 9 -4000 BeckhoffKL5001 BK5120/63/32/28/0 '
                 '-4096 230887',
        lowlevel = True,
        loadblock = loadblock
    ),
    slit2vb = device('nicos.devices.vendor.caress.Motor',
        description = 'Slit 2 Vertical Bottom',
        fmtstr = '%.2f',
        unit = 'mm',
        # 2018-10-03 coderoffset was changed (was 0 before). Encoder-zero-point shifted (wobble at motor-encoder joint).
        coderoffset = 12.5,
        abslimits = (-60, 60),
        nameserver = '%s' % (nameservice,),
        objname = '%s' % (servername),
        config = 'MB2VB 500 nist222dh1787.hmi.de:/st222.caress_object '
                 'CopleyStepnet 10 4000 BeckhoffKL5001 BK5120/63/32/32/0 '
                 '4096 258251',
        lowlevel = True,
        loadblock = loadblock
    ),
    slit2vt = device('nicos.devices.vendor.caress.Motor',
        description = 'Slit 2 Vertical Top',
        fmtstr = '%.2f',
        unit = 'mm',
        # 2018-10-03 coderoffset was changed (was 0 before). Encoder-zero-point shifted (wobble at motor-encode joint).
        coderoffset = 11.0,
        abslimits = (-60, 60),
        nameserver = '%s' % (nameservice,),
        objname = '%s' % (servername),
        config = 'MB2VT 500 nist222dh1787.hmi.de:/st222.caress_object '
                 'CopleyStepnet 11 4000 BeckhoffKL5001 BK5120/63/32/36/0 '
                 '4096 352590',
        lowlevel = True,
        loadblock = loadblock
    ),
    slit2 = device('nicos.devices.generic.Slit',
        description = 'Slit 2',
        left = 'slit2hl',
        right = 'slit2hr',
        top = 'slit2vt',
        bottom = 'slit2vb',
        opmode = 'offcentered',
        coordinates = 'equal',
    ),
)
