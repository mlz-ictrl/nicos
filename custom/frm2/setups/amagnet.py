description = 'ANTARES garfield magnet'

group = 'plugplay'

includes = ['alias_B']

tango_base = 'tango://%s:10000/box/' % setupname

devices = dict(
    amagnet_onoff = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Garfield magnet: on/off switch',
        tangodevice = tango_base + 'plc/_enable',
        mapping = dict(
            on = 1, off = 0
        ),
    ),
    amagnet_polarity = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Garfield magnet: polarity (+/-) switch',
        tangodevice = tango_base + 'plc/_polarity',
        # 0 is shorting the power-supply: only if current is zero!
        # there is an interlock in the plc:
        # if there is current, switching polarity is forbidden
        # if polarity is short, powersupply is disabled
        mapping = {'+1': 1,
                   '0': 0,
                   '-1': -1},
    ),
    amagnet_symmetry = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Garfield magnet: par/ser switch selecting (a)symmetric mode',
        tangodevice = tango_base + 'plc/_symmetric',
        # symmetric is ser, asymmetric is par
        mapping = dict(
            symmetric = 1, short = 0, unsymmetric = -1
        ),
    ),
    amagnet_T1 = device('nicos.devices.tango.AnalogInput',
        description = 'Temperature1 of the coils system',
        tangodevice = tango_base + 'plc/_t1',
        unit = 'degC',
        warnlimits = (0, 50),
    ),
    amagnet_T2 = device('nicos.devices.tango.AnalogInput',
        description = 'Temperature2 of the coils system',
        tangodevice = tango_base + 'plc/_t2',
        unit = 'degC',
        warnlimits = (0, 50),
    ),
    amagnet_T3 = device('nicos.devices.tango.AnalogInput',
        description = 'Temperature3 of the coils system',
        tangodevice = tango_base + 'plc/_t3',
        unit = 'degC',
        warnlimits = (0, 50),
    ),
    amagnet_T4 = device('nicos.devices.tango.AnalogInput',
        description = 'Temperature4 of the coils system',
        tangodevice = tango_base + 'plc/_t4',
        unit = 'degC',
        warnlimits = (0, 50),
    ),
    amagnet_current = device('nicos.devices.tango.PowerSupply',
        description = 'Device for the magnet power supply (current mode)',
        tangodevice = tango_base + 'lambda/curr',
        unit = 'A',
        abslimits = (0, 200),
        precision = 0.05,
    ),
    # by convention this needs to be B_%(setupname)s
    B_amagnet = device('frm2.amagnet.GarfieldMagnet',
        description = 'magnetic field device, handling polarity switching and stuff',
        currentsource = 'amagnet_current',
        onoffswitch = 'amagnet_onoff',
        polswitch = 'amagnet_polarity',
        symmetry = 'amagnet_symmetry',
        unit = 'T',
        # B(I) = c[0]*I + c[1]*erf(c[2]*I) + c[3]*atan(c[4]*I)
        # 2016/10/12: Kalibrierkuve.xls from T.Reimann
        calibrationtable = dict(
            symmetric = (
                0.00186517, 0.0431937, -0.185956, 0.0599757, 0.194042
            ),
            short = (0.0, 0.0, 0.0, 0.0, 0.0),
            unsymmetric = (
                0.00136154, 0.027454, -0.120951, 0.0495289, 0.110689
            ),
        ),
        userlimits = (-0.35, 0.35),
    ),
)

alias_config = {'B': {'B_amagnet': 100},}
