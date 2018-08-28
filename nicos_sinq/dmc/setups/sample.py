description = 'Sample devices in the SINQ DMC.'

pvprefix = 'SQ:DMC:mota:'

devices = dict(
    som=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample omega motor',
               motorpv=pvprefix + 'SOM',
               errormsgpv=pvprefix + 'SOM-MsgTxt',
               )
)
