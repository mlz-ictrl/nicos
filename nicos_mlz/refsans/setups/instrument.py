description = 'origin'

group = 'configdata'

instrument_name = 'refsans'
facility = 'mlz'
master = 'tum'
tdl = 'de'
Softwaresytem = 'nicos'
geografical_place = 'frm2'
tango_port = 10000
pc_hw = '%shw' % instrument_name
pc_ctrl = '%sctrl' % instrument_name

values = {
    'instrument_name': instrument_name,
    'nethost': '%ssrv.%s.%s'% (
                instrument_name,
                instrument_name,
                geografical_place,
                ),
    'pc_hw': pc_hw,
    'pc_hw_real1': '%sctrl02' % instrument_name,
    'pc_hw_real2': '',
    'pc_ctrl': '%sctrl.%s.%s.%s.%s' % (
          instrument_name,
          instrument_name,
          geografical_place,
          master,
          tdl,
          ),
    'pc_ctrl_real1': '%sctrl01' % instrument_name,
    'pc_ctrl_real2': '',
    'tango_base': 'tango://%s.%s.%s.%s.%s:%d/' % (
          pc_hw,
          instrument_name,
          geografical_place,
          master,
          tdl,
          tango_port,
          ),
    'url_base': 'http://%%s.%s.%s/' % (
          instrument_name,
          geografical_place,
          ),
    'code_base': '%s_%s.%s.devices.' % (
          Softwaresytem,
          facility,
          instrument_name,
          ),
}
