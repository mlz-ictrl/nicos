description = 'LoKI Sample Environments'

group = 'optional'

devices = dict(
    cellholder_y_motor=device('nicos.devices.generic.virtual.VirtualMotor',
        description='Motor for moving cellholder vertically',
        fmtstr="%7.2f",
        userlimits=(0, 50),
        abslimits=(0, 50),
        curvalue=0,
        unit='mm',
        speed=5.,
        visibility=(),
    ),
    cellholder_x_motor=device('nicos.devices.generic.virtual.VirtualMotor',
        description='Motor for moving cellholder horizontally',
        fmtstr="%7.2f",
        userlimits=(0, 500),
        abslimits=(0, 500),
        curvalue=0,
        unit='mm',
        speed=5.,
        visibility=(),
    ),
    thermostated_cellholder=device('nicos_ess.loki.devices.thermostated_cellholder.ThermoStatedCellHolder',
        description='The thermostated cell-holder for LoKI',
        xmotor='cellholder_x_motor',
        ymotor='cellholder_y_motor',
        precision=[0.05, 0.05],
    ),
)
