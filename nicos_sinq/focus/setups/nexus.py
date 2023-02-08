description = 'setup for NeXus file writing'

sysconfig = dict(datasinks = ['nxsink'])

excludes = ['ascii']

devices = dict(
    nxfw = device('nicos.devices.generic.ManualSwitch',
        description = 'Switch for enabling/disabling NeXus file writing',
        states = ['on', 'off']
    ),
    nxsink = device('nicos_sinq.devices.datasinks.SwitchableNexusSink',
        file_switch = 'nxfw',
        description = 'Sink for NeXus file writer',
        filenametemplate = ['focus%(year)sn%(scancounter)06d.hdf'],
        templateclass =
        'nicos_sinq.focus.nexus.nexus_templates.FOCUSTemplateProvider',
    ),
)
startupcode = """
Exp._setROParam('forcescandata', True)
"""
