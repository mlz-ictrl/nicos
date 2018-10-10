description = "SPODI setup for STRESS-SPEC's Newport Eulerian cradle"

group = 'optional'

excludes = ['tensile']

servername = 'VMESPODI'

nameservice = 'spodisrv.spodi.frm2'

devices = dict(
    chit = device('nicos.devices.vendor.caress.EKFMotor',
        description = 'HWB CHIT',
        fmtstr = '%.2f',
        unit = 'deg',
        # coderoffset = -808.11,
        abslimits = (-1, 91),
        nameserver = '%s' % nameservice,
        objname = '%s' % servername,
        config = 'CHIT 115 11 0x00f1d000 1 32096 8000 800 1 0 0 '
                 '1 0 1 5000 1 10 0 0 0',
        # config = 'CHIN 114 11 0x00f1e000 3 20480 8000 800 2 24 50 '
        #         '-1 0 1 5000 1 10 0 0 0',
    ),
)
