description = 'detector moving devices'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    det_drift = device('nicos.devices.generic.ManualSwitch',
        description = 'depth of detector drift1=40mm drift2=65mm',
        states = ['off','drift1', 'drift2'],
    ),
    det_pivot = device('nicos_mlz.refsans.devices.pivot.PivotPoint',
        description = 'Pivot point at floor of samplechamber',
        states = [i for i in range(1, 14 + 1)],
        fmtstr = '%d',
        unit = '. Point',
    ),
    table_z_motor = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorDetector',
        description = 'table inside tube',
        tacodevice = '//%s/test/modbus/tablee'% (nethost,),
        address = 0x3020 + 0 * 10,  # word address
        slope = 100,
        unit = 'mm',
        abslimits = (1000, 11025),  # because of Beamstop
        precision = 10,
        lowlevel = True,
    ),
    table_z_obs = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffCoderDetector',
        description = 'Coder of detector table inside tube',
        tacodevice = '//%s/test/modbus/tablee'% (nethost,),
        address = 0x3020 + 1 * 10,  # word address
        slope = 100,
        unit = 'mm',
        lowlevel = True,
    ),
    det_table_a = device('nicos.devices.generic.Axis',
        description = 'detector table inside tube. absmin is for beamstop',
        motor = 'table_z_motor',
        obs = ['table_z_obs'],
        precision = 1,
        dragerror = 15.,
        lowlevel = True,
    ),
    det_table = device('nicos_mlz.refsans.devices.focuspoint.FocusPoint',
        description = 'detector table inside tube. with pivot',
        unit = 'mm',
        table = 'det_table_a',
        pivot = 'det_pivot',
    ),
    tube_m = device('nicos.devices.taco.Motor',
        description = 'tube Motor',
        tacodevice = '%s/servostar/tube0' % tacodev,
        abslimits = (-200, 1000),
        lowlevel = True,
    ),
    det_yoke = device('nicos.devices.generic.Axis',
        description = 'tube height',
        motor = 'tube_m',
        obs = [],
        precision = 0.05,
        dragerror = 10.,
    ),
)
