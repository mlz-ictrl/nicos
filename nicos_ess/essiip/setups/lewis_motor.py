description = 'Lewis Motor setup.'

devices = dict(
    stat=device('nicos.devices.epics_ng.EpicsReadable',
                description='Status PV of Lewis Motor1.',
                lowlevel=True,
                readpv='Motor1:Stat'),
    spd=device('nicos.devices.epics_ng.EpicsAnalogMoveable',
               description='Speed PV of Lewis Motor1.',
               lowlevel=True,
               readpv='Motor1:Spd', writepv='Motor1:Spd'),
    stop=device('nicos.devices.epics_ng.EpicsDigitalMoveable',
                description='Stop PV of Lewis Motor1.',
                lowlevel=True,
                readpv='Motor1:Stop', writepv='Motor1:Stop'),

    mot=device('nicos_ess.essiip.devices.lewis_motor.LewisEpicsMotor',
               readpv='Motor1:Pos', writepv='Motor1:Tgt',
               description='Lewis Motor.',
               status_pv='stat',
               stop_pv='stop',
               speed_pv='spd',
               ),
)
