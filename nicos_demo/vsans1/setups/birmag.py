description = 'Birmingham Magnet 17T'

group = 'optional'

includes = ['alias_B']

devices = dict(
    # B_birmag = device('nicos.devices.taco.AnalogInput',
    #     description = 'magnetic field of birmingham magnet',
    #     fmtstr = '%.3f',
    # ),
    # T_birmag_a = device('nicos.devices.taco.AnalogInput',
    #     description = 'temperature a of birmingham magnet',
    #     fmtstr = '%.3f',
    # ),
    # T_birmag_b = device('nicos.devices.taco.AnalogInput',
    #     description = 'temperature b of birmingham magnet',
    #     fmtstr = '%.3f',
    # ),
    # birmag_sp1 = device('nicos.devices.taco.AnalogInput',
    #     description = 'setpoint 1 of birmingham magnet',
    #     fmtstr = '%.3f',
    # ),
    # birmag_sp2 = device('nicos.devices.taco.AnalogInput',
    #     description = 'setpoint 2 of birmingham magnet',
    #     fmtstr = '%.3f',
    # ),
    # birmag_helevel = device('nicos.devices.taco.AnalogInput',
    #     description = 'helium level of birmingham magnet',
    #     fmtstr = '%.3f',
    # ),
)

alias_config = {
    # 'B': {'B_birmag': 100},
}
