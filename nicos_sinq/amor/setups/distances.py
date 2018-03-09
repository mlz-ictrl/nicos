description = 'Various distance settings in AMOR'

devices = dict(
    dchopper=device(
        'nicos_sinq.amor.devices.component_handler.ComponentHandler',
        description='Distance of chopper from the laser'),
    dfilter=device(
        'nicos_sinq.amor.devices.component_handler.ComponentHandler',
        description='Distance of filter from the laser', ),
    dpolarizer=device(
        'nicos_sinq.amor.devices.component_handler.ComponentHandler',
        description='Distance of monochromator from the laser',
        mirrorheight=-88.0),
    dslit1=device('nicos_sinq.amor.devices.component_handler.ComponentHandler',
                  description='Distance of slit 1 from the laser', ),
    dslit2=device('nicos_sinq.amor.devices.component_handler.ComponentHandler',
                  description='Distance of slit2 from the laser',
                  mirrorheight=-73.0),
    dslit3=device('nicos_sinq.amor.devices.component_handler.ComponentHandler',
                  description='Distance of slit3 from the laser',
                  mirrorheight=-63.0),
    dslit4=device('nicos_sinq.amor.devices.component_handler.ComponentHandler',
                  description='Distance of slit4 from the laser',
                  mirrorheight=-34.0),
    dsample=device(
        'nicos_sinq.amor.devices.component_handler.ComponentHandler',
        description='Distance of sample from the laser', mirrorheight=-52.0),
    danalyzer=device(
        'nicos_sinq.amor.devices.component_handler.ComponentHandler',
        description='Distance of analyzer from the laser', mirrorheight=-24.0),
    ddetector=device(
        'nicos_sinq.amor.devices.component_handler.ComponentHandler',
        description='Distance of detector from the laser', mirrorheight=0.0),
)
