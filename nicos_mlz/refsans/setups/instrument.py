description = 'origin'

group = 'configdata'

instrument_name = 'refsans'
facility = 'mlz'
master = 'tum'
tld = 'de'
software_system = 'nicos'
geographical_place = 'frm2'
tango_port = 10000
pc_hw = '%shw' % instrument_name
pc_ctrl = '%sctrl' % instrument_name

values = {
    'instrument_name': instrument_name,
    'pc_hw': pc_hw,
    'pc_hw_real1': '%sctrl02' % instrument_name,
    'pc_hw_real2': '',
    'pc_ctrl': '%sctrl.%s.%s.%s.%s' % (
        instrument_name,
        instrument_name,
        geographical_place,
        master,
        tld,
    ),
    'pc_ctrl_real1': '%sctrl01' % instrument_name,
    'pc_ctrl_real2': '',
    'tango_base': 'tango://%s.%s.%s.%s.%s:%d/' % (
        pc_hw,
        instrument_name,
        geographical_place,
        master,
        tld,
        tango_port,
    ),
    'tango_url': 'tango://%%s.%s.%s.%s.%s:%d/' % (
        instrument_name,
        geographical_place,
        master,
        tld,
        tango_port,
    ),
    'url_base': 'http://%%s.%s.%s.%s.%s/' % (
        instrument_name,
        geographical_place,
        master,
        tld,
    ),
    'code_base': '%s_%s.%s.devices.' % (
        software_system,
        facility,
        instrument_name,
    ),
}
