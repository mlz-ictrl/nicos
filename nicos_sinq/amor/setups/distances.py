description = 'Various distance settings in AMOR'

lowlevel = True

devices = dict(
    dchopper=device(
        'nicos_sinq.amor.devices.component_handler.ComponentLaserDistance',
        description='Distance of chopper from the laser',
        markoffset=-245.0,
        readvalue=10151.0,
        lowlevel=True),
    dfilter=device(
        'nicos_sinq.amor.devices.component_handler.ComponentLaserDistance',
        description='Distance of filter from the laser',
        markoffset=0,
        readvalue=8609.0,
        lowlevel=True),
    dpolarizer=device(
        'nicos_sinq.amor.devices.component_handler.ComponentLaserDistance',
        description='Distance of monochromator from the laser',
        markoffset=-232.0,
        readvalue=7983.0,
        lowlevel=True),
    dslit1=device(
        'nicos_sinq.amor.devices.component_handler.ComponentLaserDistance',
        description='Distance of slit 1 from the laser',
        markoffset=0.0,
        readvalue=8991.0,
        lowlevel=True),
    dslit2=device(
        'nicos_sinq.amor.devices.component_handler.ComponentLaserDistance',
        description='Distance of slit2 from the laser',
        markoffset=302.0,
        readvalue=7145.0,
        lowlevel=True),
    dslit3=device(
        'nicos_sinq.amor.devices.component_handler.ComponentLaserDistance',
        description='Distance of slit3 from the laser',
        markoffset=-22.0,
        readvalue=6445.0,
        lowlevel=True),
    dslit4=device(
        'nicos_sinq.amor.devices.component_handler.ComponentLaserDistance',
        description='Distance of slit4 from the laser',
        markoffset=306.0,
        readvalue=4210.0,
        lowlevel=True),
    dsample=device(
        'nicos_sinq.amor.devices.component_handler.ComponentLaserDistance',
        description='Distance of sample from the laser',
        markoffset=-310.0,
        readvalue=5310.0,
        lowlevel=True),
    danalyzer=device(
        'nicos_sinq.amor.devices.component_handler.ComponentLaserDistance',
        description='Distance of analyzer from the laser',
        markoffset=310.0,
        readvalue=2463.0,
        lowlevel=True),
    ddetector=device(
        'nicos_sinq.amor.devices.component_handler.ComponentLaserDistance',
        description='Distance of detector from the laser',
        markoffset=326.0,
        readvalue=572.0,
        lowlevel=True),
    dselene=device(
        'nicos_sinq.amor.devices.component_handler.ComponentLaserDistance',
        description='Distance of selene from the laser',
        markoffset=-726.0,
        readvalue=7727.0,
        lowlevel=True),
)
