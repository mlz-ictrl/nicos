description = 'HP34420 multimeter readout'
group = 'optional'

devices = dict(
    R = device('nicos.devices.taco.AnalogInput',
               description = 'multimeter readout',
               tacodevice = '//heidi22/heidi2/fluke/resistance',
              ),
)
