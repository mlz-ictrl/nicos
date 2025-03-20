description = 'Sample table devices for SINQ POLDI NEW.'
excludes = ['sample_new', 'sample_old', 'sample_zwick']
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
    # Check if the nomenclature here is correct, howcome chi/phi and alpha/beta is mixed.
    chi=device('nicos_sinq.devices.epics.motor.SinqMotor',
               description='Goniometer Alpha',
               motorpv=f'{pvprefix}CHI-EULER',
               ),
    phi=device('nicos_sinq.devices.epics.motor.SinqMotor',
               description='Rotation table Beta',
               motorpv=f'{pvprefix}PHI-EULER',
               ),
 )
