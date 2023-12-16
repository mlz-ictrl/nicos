description = 'motor driver of CASCADE detector'
group = 'optional'

tango_base = 'tango://miractrl.mira.frm2.tum.de:10000/mira/'

devices = dict(
    # co_dtx = device('nicos.devices.entangle.Sensor',
    #     visibility = (),
    #     tangodevice = tango_base + 'detector/dtx_enc',
    #     unit = 'mm',
    # ),
    mo_dtx = device('nicos.devices.entangle.Motor',
        visibility = (),
        tangodevice = tango_base + 'detector/dtx_mot',
        unit = 'mm',
        # precision = 0.1,
    ),
    dtx = device('nicos.devices.generic.Axis',
        description = 'temporary rotation table setup',
        # description = 'detector translation along the beam on Franke table',
        motor = 'mo_dtx',
        # coder = 'co_dtx',
        fmtstr = '%.1f',
        precision = 0.1,
    ),
)
