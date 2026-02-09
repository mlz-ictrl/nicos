description = 'Motors used to move the detectors'

group = 'lowlevel'

pvprefix = 'SQ:SANS-LLB:turboPmac3:'

includes = ["sample_table"] # needed for stz access in detz

devices = dict(
    dthx = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'High-angle detector translation horizontal',
        motorpv = pvprefix + 'dthx',
    ),
    dthy = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'High-angle detector translation vertical',
        motorpv = pvprefix + 'dthy',
    ),
    dthz = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'High-angle detector translation along the beam axis',
        motorpv = pvprefix + 'dthz',
    ),
    dtlx = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Low-angle detector translation horizontal',
        motorpv = pvprefix + 'dtlx',
    ),
    dtlz = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Low-angle detector translation along the beam axis',
        motorpv = pvprefix + 'dtlz',
    ),
    detz=device('nicos_sinq.sans-llb.devices.detector_coupling.SansLlbCoupledDetectors',
                description='Detectors coupled translation, position is low-angle detector distance',
                unit='mm',
                fmtstr='%.1f',
                low_angle_x='dtlx',
                low_angle_z='dtlz',
                sample_offset_z='stz',
                high_angle_x='dthx',
                high_angle_y='dthy',
                high_angle_z='dthz',
                # geometry parameters used to calculate x/y position of high angle detector:
                high_angle_opening_x=100.,
                high_angle_opening_y=336.,
                low_angle_frame_x=350.,
                low_angle_frame_y=330.,
                save_distance_z=800.,
    ),
)
