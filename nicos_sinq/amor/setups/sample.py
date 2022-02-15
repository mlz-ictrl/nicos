description = 'Sample devices in the SINQ AMOR.'

group = 'lowlevel'

pvprefix = 'SQ:AMOR:motserial:'

devices = dict(
    xs=device('nicos.devices.generic.VirtualMotor',
              description='Sample X position',
              abslimits=(100, 8000),
              curvalue=2265,
              unit='mm',
    ),
    som = device('nicos_ess.devices.epics.motor.EpicsMotor',
        description = 'Sample omega motor',
        motorpv = pvprefix + 'som',
        errormsgpv = pvprefix + 'som-MsgTxt',
    ),
    soz = device('nicos_ess.devices.epics.motor.EpicsMotor',
        description = 'Sample z lift of base motor',
        motorpv = pvprefix + 'soz',
        errormsgpv = pvprefix + 'soz-MsgTxt',
    ),
)
