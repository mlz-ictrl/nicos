description = 'Sample table devices for SINQ POLDI NEW.'
excludes = ['sample_old', 'sample_zwick', 'sample_euler']
pvprefix = 'SQ:POLDI:turboPmac1:'

devices = dict(
    sa=device('nicos_sinq.devices.epics.motor.SinqMotor',
               description='Sample table rotation',
               motorpv=f'{pvprefix}SA-NZE',
               ),
    shl=device('nicos_sinq.devices.epics.motor.SinqMotor',
               description='Sample table X translation',
               motorpv=f'{pvprefix}SHL-NE',
               ),
    shu=device('nicos_sinq.devices.epics.motor.SinqMotor',
               description='Sample table Y translation',
               motorpv=f'{pvprefix}SHU-NE',
               ),
    sv=device('nicos_sinq.devices.epics.motor.SinqMotor',
               description='Sample table hub Z translation',
               motorpv=f'{pvprefix}SV',
               ),
 )
