description = 'FRM-II FAK40 information (cooling water system)'

group = 'lowlevel'
nethost = 'tacodb.taco.frm2'

devices = dict(
        FAK40_Cap = device('devices.taco.AnalogInput',
                           tacodevice = '//%s/frm2/fak40/capacity' % (nethost, ),
                           description = 'The capacity of the cooling water system',
                           pollinterval = 60,
                           maxage = 120,
                          ),
        FAK40_Press = device('devices.taco.AnalogInput',
                             tacodevice = '//%s/frm2/fak40/pressure' % (nethost, ),
                             description = 'The pressure inside the cooling water system',
                             pollinterval = 60,
                             maxage = 120,
                            ),
)
