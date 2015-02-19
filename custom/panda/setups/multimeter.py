description = 'HP34420 multimeter readout'
group = 'optional'

devices = dict(
    R = device('devices.taco.AnalogInput',
               description = 'multimeter readout',
               tacodevice = '//pandasrv/panda/hp34420/resistance',
              ),
)
