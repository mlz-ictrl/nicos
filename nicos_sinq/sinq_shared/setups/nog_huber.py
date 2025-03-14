description = 'Neutron Optic Gurke with Huber motors'

pvprefix = 'SQ:BOA:optics:'

devices = dict(
    nog_t1 = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'NOG Translation 1',
        motorpv = pvprefix + 'trans1',
        errormsgpv = pvprefix + 'trans1-MsgTxt',
        precision = 0.05,
        can_disable = False,
    ),
    nog_t2 = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'NOG Translation 2',
        motorpv = pvprefix + 'trans2',
        errormsgpv = pvprefix + 'trans2-MsgTxt',
        precision = 0.05,
        can_disable = False,
    ),
    nog_lift1 = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'NOG lift 1',
        motorpv = pvprefix + 'lift1',
        errormsgpv = pvprefix + 'lift1-MsgTxt',
        precision = 0.05,
        can_disable = False
    ),
    nog_lift2 = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'NOG lift2 2',
        motorpv = pvprefix + 'lift2',
        errormsgpv = pvprefix + 'lift2-MsgTxt',
        precision = 0.05,
        can_disable = False,
    ),
    nog_vert_dir = device('nicos_sinq.devices.noptic.NODirector',
        description = 'Coordinate the vertical movement',
        m1 = 'nog_lift1',
        m2 = 'nog_lift2',
        maxdiv = 5,
        m1_length = 210,
        m2_length = 628,
        unit = 'degree',
    ),
    nog_hor_dir = device('nicos_sinq.devices.noptic.NODirector',
        description = 'Coordinate the horizontal movement',
        m1 = 'nog_t1',
        m2 = 'nog_t2',
        maxdiv = 13,
        m1_length = 59,
        m2_length = 517.5,
        unit = 'degree',
    ),
    nog_v_pos = device('nicos.devices.generic.ParamDevice',
        description = 'NOG vertical position',
        device = 'nog_vert_dir',
        parameter = 'position',
        copy_status = True,
    ),
    nog_v_tilt = device('nicos.devices.generic.ParamDevice',
        description = 'NOG vertical tilt',
        device = 'nog_vert_dir',
        parameter = 'tilt',
        copy_status = True,
    ),
    nog_h_pos = device('nicos.devices.generic.ParamDevice',
        description = 'NOG horizontal position',
        device = 'nog_hor_dir',
        parameter = 'position',
        copy_status = True,
    ),
    nog_h_tilt = device('nicos.devices.generic.ParamDevice',
        description = 'NOG vertical tilt',
        device = 'nog_hor_dir',
        parameter = 'tilt',
        copy_status = True,
    ),
)
