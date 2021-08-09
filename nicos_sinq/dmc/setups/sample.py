description = 'Sample devices in the SINQ DMC.'

pvprefix = 'SQ:DMC:mcu2:'

devices = dict(
    a3=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample omega motor',
               motorpv=f'{pvprefix}SOM',
               errormsgpv=f'{pvprefix}SOM-MsgTxt',
               ),
)
