description = 'Slit 3 devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:motc:'

includes = ['slit1']

devices = dict(
    d3t=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Slit 3 opening motor',
               motorpv=pvprefix + 'd3t',
               errormsgpv=pvprefix + 'd3t-MsgTxt',
               lowlevel=True
               ),
    d3b=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Slit 3 z position (lower edge) motor',
               motorpv=pvprefix + 'd3b',
               errormsgpv=pvprefix + 'd3b-MsgTxt',
               lowlevel=True
               ),
    slit3=device('nicos.devices.generic.slit.Slit',
                 description='Slit 3 with left, right, bottom and top motors',
                 opmode='4blades',
                 left='d1l',
                 right='d1r',
                 top='d3t',
                 bottom='d3b',
                 ),
    slit3_opening=device('nicos_sinq.amor.devices.slit.SlitOpening',
                         description='Slit 3 opening controller',
                         slit='slit3'
                         ),
)
