description = 'Rotation Table via CARESS'


servername = 'EXV20'
nameservice = '192.168.1.254'
loadblock='''read=always,async
'''

devices = dict(
    pol_rot = device('nicos.devices.vendor.caress.Motor',
        description = 'POL_ROT via CARESS',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = 0,
        abslimits = (-720, 720),
        nameserver = nameservice,
        objname = servername,
        config = 'POL_ROT 500 nist222dh1787.hmi.de:/st222.caress_object '
                 'CopleyStepnet 12 4000 CopleyStepnet 12 4000 0',
        loadblock = loadblock,
    ),
)

