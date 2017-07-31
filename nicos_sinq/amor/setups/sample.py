description = 'Sample devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:mota:'

devices = dict(
    som=device('nicos_ess.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample omega motor',
               motorpv=pvprefix + 'som',
               ),
    soz=device('nicos_ess.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample z lift of base motor',
               motorpv=pvprefix + 'soz',
               ),
    stz=device('nicos_ess.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample z translation on sample table motor',
               motorpv=pvprefix + 'stz',
               ),
    sch=device('nicos_ess.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample chi motor',
               motorpv=pvprefix + 'sch',
               ),
)
