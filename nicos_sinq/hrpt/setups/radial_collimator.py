description= 'HRPT Radial Collimator'

pvprefix='SQ:HRPT:radicol:'

devices = dict(
        racoll=device('nicos_sinq.hrpt.devices.radialcollimator.RadialCollimator',
                   basepv=pvprefix,
                   mapping=dict({'on' : 1,'off' : 0}),
                   description='HRPT Radial Collimator',
                   epicstimeout= 10.0,
                   )

    )
