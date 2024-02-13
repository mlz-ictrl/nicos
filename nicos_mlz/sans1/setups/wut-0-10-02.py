description = 'W&T Box * 0-10V * Nr. 2'

_wutbox_dev = setupname.replace('-','_')

devices = {
    _wutbox_dev + '_1': device('nicos_mlz.sans1.devices.wut.WutReadValue',
        hostname = f'{setupname}.sans1.frm2.tum.de',
        port = 1,
        description = 'input 1 voltage',
        fmtstr = '%.3F',
        loglevel = 'info',
        pollinterval = 5,
        maxage = 20,
        unit = 'V',
    ),
    _wutbox_dev + '_2': device('nicos_mlz.sans1.devices.wut.WutReadValue',
        hostname = f'{setupname}.sans1.frm2.tum.de',
        port = 2,
        description = 'input 2 voltage',
        fmtstr = '%.3F',
        loglevel = 'info',
        pollinterval = 5,
        maxage = 20,
        unit = 'V',
    ),
}
