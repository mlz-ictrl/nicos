description = 'origin'

group = 'configdata'

instrument_name = 'xresd'
hw_uri = 'rsxrd.softlab.frm2.tum.de'
tango_port = 10000
facility = 'mlz'
software_system = 'nicos'

values = {
    'instrument_name': instrument_name,
    'tango_base': 'tango://%s:%d/' % (
        hw_uri,
        tango_port,
    ),
    'code_base': '%s_%s.%s.devices.' % (
        software_system,
        facility,
        instrument_name,
    ),
}
