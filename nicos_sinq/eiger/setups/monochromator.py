description = 'These are the devices for the EIGER monochromator'

mcu1prefix = 'SQ:EIGER:turboPmac1:'
mcu2prefix = 'SQ:EIGER:turboPmac2:'

devices = dict(
    a1 = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Monochromator omega',
        motorpv = mcu1prefix + 'a1',
    ),
    a2_raw = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Monochromator two theta',
        motorpv = mcu1prefix + 'a2rot',
        visibility = {'metadata'},
    ),
    mch = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Monochromator horizontal curvature',
        motorpv = mcu1prefix + 'mch',
    ),
    mcv = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Monochromator vertical curvature',
        motorpv = mcu1prefix + 'mcv',
    ),
    mt = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Monochromator translation',
        motorpv = mcu1prefix + 'mt',
    ),
    mg = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Monochromator goniometer',
        motorpv = mcu1prefix + 'mg',
    ),
    d2l = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Monochromator out left slit blade',
        motorpv = mcu2prefix + 'd2l',
    ),
    d2r = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Monochromator out right slit blade',
        motorpv = mcu2prefix + 'd2r',
    ),
    a2controller = device('nicos_sinq.eiger.devices.eigermono.EigerA2Controller',
        description = 'Controller for aligning A2 and A2 slits',
        reala2 = 'a2_raw',
        left = 'd2l',
        right = 'd2r',
        visibility = (),
    ),
    a2 = device('nicos_sinq.devices.logical_motor.LogicalMotor',
        description = 'Logical A2 motor',
        controller = 'a2controller',
        abslimits = (17, 90.14)
    ),
    a2w = device('nicos_sinq.devices.logical_motor.LogicalMotor',
        description = 'Logical out slit width',
        controller = 'a2controller',
        abslimits = (0, 20.)
    ),
    a2seg = device('nicos.devices.epics.pva.epics_devices.EpicsReadable',
        description = 'A2 Segment Width',
        readpv = mcu1prefix + 'a2seg.RBV',
        monitor = True,
    ),
    mono = device('nicos_sinq.eiger.devices.eigermono.EigerMonochromator',
        description = 'EIGER monochromator',
        theta = 'a1',
        twotheta = 'a2',
        material = 'PG',
        reflection = (0, 0, 2),
        dvalue = 3.354,
        scatteringsense = 1,
        crystalside = 1,
        unit = 'meV',
        focmode = 'double',
        vfocuspars = [-0.08, 1.04],
        hfocuspars = [78.03, 190.3],
        abslimits = [1.5, 80],
        focusv = 'mcv',
        focush = 'mch',
        mt = 'mt'
    ),
    ei = device('nicos.core.device.DeviceAlias',
        description = 'Alias for driving the monochromator',
        alias = 'mono',
    ),
)
