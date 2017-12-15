description = 'REFSANS setup for julabo+rs232-5_05.res'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    #
    ## rs232server julabo exports
    #
    # rs232_julabo = device('unknown_class:StringIO',
    #     description = 'Device test/rs232/julabo of Server rs232server julabo',
    #     tacodevice = '//%s/test/rs232/julabo' % nethost,
    # ),

    #
    ## julaboserver julabo01 exports
    #
    julabo_temp = device('nicos.devices.taco.TemperatureController',
        description = 'Device test/julabo/temp of Server julaboserver julabo01',
        tacodevice = '//%s/test/julabo/temp' % nethost,
        abslimits = (0, 500),
    ),
)
