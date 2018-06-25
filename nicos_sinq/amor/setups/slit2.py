description = 'Slit 2 devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:motc:'

includes = ['slit1']

devices = dict(
    d2t=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Slit 2 opening motor',
               motorpv=pvprefix + 'd2t',
               errormsgpv=pvprefix + 'd2t-MsgTxt',
               lowlevel=True
               ),
    d2b=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Slit 2 z position (lower edge) motor',
               motorpv=pvprefix + 'd2b',
               errormsgpv=pvprefix + 'd2b-MsgTxt',
               lowlevel=True
               ),
    slit2=device('nicos.devices.generic.slit.Slit',
                 description='Slit 2 with left, right, bottom and top motors',
                 opmode='4blades',
                 left='d1l',
                 right='d1r',
                 top='d2t',
                 bottom='d2b',
                 ),
    slit2_opening=device('nicos_sinq.amor.devices.slit.SlitOpening',
                         description='Slit 2 opening controller',
                         slit='slit2'
                         ),
)
