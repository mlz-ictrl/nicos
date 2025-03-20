description = 'Sample table devices for SINQ POLDI OLD.'
excludes = ['sample_old', 'sample_new', 'sample_euler']
pvprefix = 'SQ:POLDI:turboPmac1:'

devices = dict(
    sa=device('nicos_sinq.devices.epics.motor.SinqMotor',
               description='Sample table rotation',
               motorpv=f'{pvprefix}SA-NZE',
               ),
    shl=device('nicos_sinq.devices.epics.motor.SinqMotor',
               description='Sample table X translation',
               motorpv=f'{pvprefix}SHL-ZWICK',
               ),
    shu=device('nicos_sinq.devices.epics.motor.SinqMotor',
               description='Sample table Y translation',
               motorpv=f'{pvprefix}SHU-ZWICK',
               ),
    sv=device('nicos_sinq.devices.epics.motor.SinqMotor',
               description='Sample table hub Z translation',
               motorpv=f'{pvprefix}SV',
               ),
 )
