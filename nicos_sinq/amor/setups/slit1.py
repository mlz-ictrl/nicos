description = 'Slit 1 devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:motc:'

devices = dict(
    d1l=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Slit 1 left motor',
               motorpv=pvprefix + 'd1l',
               errormsgpv=pvprefix + 'd1l-MsgTxt',
               lowlevel=True
               ),
    d1r=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Slit 1 right motor',
               motorpv=pvprefix + 'd1r',
               errormsgpv=pvprefix + 'd1r-MsgTxt',
               lowlevel=True
               ),
    d1t=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Slit 1 opening motor',
               motorpv=pvprefix + 'd1t',
               errormsgpv=pvprefix + 'd1t-MsgTxt',
               lowlevel=True
               ),
    d1b=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Slit 1 z position (lower edge) motor',
               motorpv=pvprefix + 'd1b',
               errormsgpv=pvprefix + 'd1b-MsgTxt',
               lowlevel=True
               ),
    slit1=device('nicos.devices.generic.slit.Slit',
                 description='Slit 1 with left, right, bottom and top motors',
                 opmode='4blades',
                 left='d1l',
                 right='d1r',
                 top='d1t',
                 bottom='d1b',
                 ),
    slit1_opening=device('nicos_sinq.amor.devices.slit.SlitOpening',
                         description='Slit 1 opening controller',
                         slit='slit1'
                         ),
    slit1_width=device('nicos.devices.generic.slit.WidthSlitAxis',
                       description='Slit 1 width controller',
                       slit='slit1',
                       unit='mm',
                       lowlevel=True
                       ),
)
