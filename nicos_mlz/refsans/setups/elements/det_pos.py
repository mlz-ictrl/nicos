description = 'detector moving devices'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    det_pivot = device('nicos.devices.generic.ManualSwitch',
        description = 'Pivot point at floor of samplechamber',
        states = range(1, 14 + 1),
        fmtstr = 'Point %d',
        unit = '',
    ),
    # according to docu: 'Anhang_A_REFSANS_Cab1 ver25.06.2014 0.1.3 mit nok5b.pdf'
    # according to docu: '_2013-04-08 Anhang_A_REFSANS_Schlitten V0.7.pdf'
    # according to docu: '_2013-04-05 Anhang A V0.6.pdf'
    # according to docu: '_Anhang_A_REFSANS_Pumpstand.pdf'
    # according to '_2013-04-08 Anhang_A_REFSANS_Schlitten V0.7.pdf'
    # det_z is along the scattered beam (inside the tube)
    # beckhoff is at 'detektorantrieb.refsans.frm2' / 172.25.18.108
    table_z_motor = device('nicos_mlz.refsans.devices.beckhoff.nok.BeckhoffMotorDetector',
        description = 'table inside tube',
        tacodevice = '//%s/test/modbus/tablee'% (nethost,),
        address = 0x3020 + 0 * 10,  # word address
        slope = 100,
        unit = 'mm',
        # according to docu:
        abslimits = (620, 11025),
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
    det_table = device('nicos.devices.generic.Axis',
        description = 'detector table inside tube',
        motor = 'table_z_motor',
        obs = ['table_z_obs'],
        precision = 1,
        dragerror = 10.,
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
