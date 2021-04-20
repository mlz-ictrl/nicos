description = 'Monochromator device setup'

group = 'lowlevel'

# servername = 'VMESPODI'

# nameservice = 'spodisrv.spodi.frm2'

tango_base = 'tango://motorbox02.spodi.frm2.tum.de:10000/box/'

devices = dict(
    # ;Monochromator
    omgm = device('nicos.devices.entangle.Motor',
        description = 'HWB OMGM',
        tangodevice = tango_base + 'omgm/motor',
        fmtstr = '%.3f',
        unit = 'deg',
        userlimits = (-10, 10),
    ),
    tthm = device('nicos.devices.generic.ManualSwitch',
        description = 'HWB TTHM',
        fmtstr = '%.3f',
        unit = 'deg',
        states = (155.,),
    ),
    # chim = device('nicos.devices.vendor.caress.EKFMotor',
    #     description = 'HWB CHIM',
    #     fmtstr = '%.2f',
    #     unit = 'deg',
    #     coderoffset = 2928.3,
    #     abslimits = (-3, 3),
    #     nameserver = '%s' % nameservice,
    #     objname = '%s' % servername,
    #     config = 'CHIM 114 11 0x00f1e000 1 8192 6000 200 2 25 50 '
    #              '-1 0 1 5300 1 10 10 0 1000',
    # ),
    # zm = device('nicos.devices.vendor.caress.EKFMotor',
    #     description = 'HWB ZM',
    #     fmtstr = '%.2f',
    #     unit = 'mm',
    #     coderoffset = -6347.84,
    #     abslimits = (0, 220),
    #     nameserver = '%s' % nameservice,
    #     objname = '%s' % servername,
    #     config = 'ZM 114 11 0x00f1d000 2 4096 6000 200 2 25 50 '
    #              '1 0 1 3360 1 10 10 0 500',
    # ),
    # ym = device('nicos.devices.vendor.caress.EKFMotor',
    #     description = 'HWB YM',
    #     fmtstr = '%.2f',
    #     unit = 'mm',
    #     coderoffset = -2043.89,
    #     abslimits = (-15, 15),
    #     nameserver = '%s' % nameservice,
    #     objname = '%s' % servername,
    #     config = 'YM 114 11 0x00f1d000 3 4096 6000 200 2 25 50 '
    #              '1 0 1 5300 1 10 10 0 500',
    # ),
    # xm = device('nicos.devices.vendor.caress.EKFMotor',
    #     description = 'HWB XM',
    #     fmtstr = '%.2f',
    #     unit = 'mm',
    #     coderoffset = -5852.43,
    #     abslimits = (-15, 15),
    #     nameserver = '%s' % nameservice,
    #     objname = '%s' % servername,
    #     config = 'XM 114 11 0x00f1d000 4 4096 6000 200 2 25 50 '
    #              '1 0 1 5300 1 10 10 0 500',
    # ),
)
