description = 'Helios 3He analyzer system'
group = 'plugplay'

devices = {
    'flipper_%s' % setupname : device('nicos_mlz.frm2.helios.HePolarizer',
                   description = 'polarization direction of Helios cell with RF flipper',
                   tangodevice = 'tango://%s:10000/box/helios/flipper' % setupname
                  ),
}
