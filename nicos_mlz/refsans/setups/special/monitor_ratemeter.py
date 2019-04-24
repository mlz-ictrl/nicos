# created by MP
# 04.12.2017 07:53:39
# to call it
# ssh refsans@refsansctrl01 oder 02
# INSTRUMENT=nicos_mlz.refsans bin/nicos-monitor -S monitor_mp-PO
# not perfet but working

description = 'Ratemeter'
group = 'special'

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = description,
        loglevel = 'info',
        cache = 'refsanssw.refsans.frm2',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 48,
        padding = 5,
        layout = [
            Row(
                Column(
                    Block('ratemeter', [
                        BlockRow(Field(name='s d s',dev='sds',width=20, unit='cps'),),
                                       ],
                         ),
                      )
               ),
                 ],
                    ),
              )
