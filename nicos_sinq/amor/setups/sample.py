description = 'Sample devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:mota:'

devices = dict(
    som=device('nicos_ess.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample omega motor',
               motorpv=pvprefix + 'som',
               errormsgpv=pvprefix + 'som-MsgTxt',
               ),
    soz=device('nicos_ess.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample z lift of base motor',
               motorpv=pvprefix + 'soz',
               errormsgpv=pvprefix + 'soz-MsgTxt',
               ),
    stz=device('nicos_ess.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample z translation on sample table motor',
               motorpv=pvprefix + 'stz',
               errormsgpv=pvprefix + 'stz-MsgTxt',
               ),
    sch=device('nicos_ess.essiip.devices.epics_motor.EpicsMotor',
               epicstimeout=3.0,
               description='Sample chi motor',
               motorpv=pvprefix + 'sch',
               errormsgpv=pvprefix + 'sch-MsgTxt',
               ),
)
