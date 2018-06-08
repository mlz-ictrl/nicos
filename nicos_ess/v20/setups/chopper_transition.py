description = 'Chopper transition'

servername = 'EXV20'
nameservice = '192.168.1.254'
loadblock = '''read=always,async
'''

devices = dict(
    mtus = device('nicos.devices.vendor.caress.Motor',
        description = 'MTUS CARESS',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = 0,
        abslimits = (-184, -32),
        nameserver = nameservice,
        objname = servername,
        config = 'MTUS 500 nist222dh1787.hmi.de:/st222.caress_object '
                 'CopleyStepnet 1 -7272.727273 BeckhoffKL5001 BK5120/63/32/0/0 824 4151568',
        loadblock = loadblock,
    ),

    mtds = device('nicos.devices.vendor.caress.Motor',
        description = 'MTDS CARESS',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = 0,
        abslimits = (34, 189),
        nameserver = nameservice,
        objname = servername,
        config = 'MTDS 500 nist222dh1787.hmi.de:/st222.caress_object '
                 'CopleyStepnet 7 7272.727273 BeckhoffKL5001 BK5120/63/32/4/0 -819 4154609',
        loadblock = loadblock,
    ),

)

