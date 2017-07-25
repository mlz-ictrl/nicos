description = 'Julabo bio furnace'

group = 'optional'

includes = ['alias_T']

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    T_bio = device('nicos_mlz.toftof.devices.julabo.Controller',
                   description = 'Julabo temperature controller',
                   tacodevice = '//%s/toftof/rs232/ifbiofurnace' % (nethost,),
                   intern_extern = 0,
                   userlimits = (-40, 160),
                   abslimits = (-50, 200),
                   unit = 'degC',
                   fmtstr = '%g',
                  ),
)

alias_config = {
    'T': {'T_bio': 200},
    'Ts': {'T_bio': 100},
}
