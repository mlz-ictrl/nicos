# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

import os
import re
from os import path

from docutils import nodes
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.util.compat import Directive
from sphinx.util.docstrings import prepare_docstring

EXCLUDE_PARAMS = set(['description', 'passwd', 'target'])


def escape_rst(s, rex=re.compile('([`*:])')):
    return rex.sub(r'\\\1', s)


###############################################################################
##                                 Directives                                ##
###############################################################################

#
# Rst snippets
#
rstSnipSetupLink = ''':ref:`%(setupname)s <%(setuplink)s>`'''
rstSnipModuleLink = ':mod:`%(modpath)s`'
rstSnipParamLink = '`~%(classname)s.%(paramname)s`'
rstSnipGroup = '''| **Setup group:** :ref:`%(group)s <setup_group>`'''
rstSnipIncludes = '''| **Included setups:** %(includes)s'''
rstSnipExcludes = '''| **Excluded setups:** %(excludes)s'''
rstSnipModules = '''| **Used modules:** %(modules)s'''
rstSnipDevices = '''
Devices
-------

'''

rstSnipStartupcode = '''
Startup code
------------

::

    %(startupcode)s
'''

rstSnipSetup = '''
.. _%(unique_id)s:

%(setupname)s
%(setupname_underline)s

*File: %(basepath)s*

%(description)s

%(rst_group)s
%(rst_includes)s
%(rst_excludes)s
%(rst_modules)s

%(rst_devices)s

%(rst_startupcode)s
'''

devClassCache = {}  # cache for already imported device classes


class SetupDirective(Directive):

    has_content = False
    required_arguments = 1

    indention = '    '

    def run(self):
        # simplify logging access
        self.env = self.state.document.settings.env
        self.warn = self.env.app.warn

        # relative to the doc source dir
        rel_path = path.join(self.env.config.setupdoc_setup_base_dir,
                             self.arguments[0])

        # note actual setup as dependency
        self.env.note_dependency(rel_path)

        info = self._readSetup(rel_path, self.arguments[0])
        node = nodes.paragraph()
        if info:
            content = self._buildSetupRst(info)
            content = ViewList(content.splitlines(), rel_path)
            nested_parse_with_titles(self.state, content, node)

        return node.children

    def _readSetup(self, rel_path, base_path):
        # self.debug('Handle setup: %s' % rel_path)
        full_path = path.join(self.env.srcdir, rel_path)

        if not full_path.endswith('.py'):
            self.warn('Given setup is not a python file: %s' % full_path)
            return None

        setup_name = path.basename(rel_path)[:-3]

        try:
            with open(full_path, 'r') as modfile:
                code = modfile.read()
        except (ImportError, IOError) as e:
            self.warn('Error while reading setup: %s (%s)' % (full_path, str(e)))
            return None

        ns = {
              'device': lambda cls, **params: (cls, params),
              'setupname' : setup_name
              }

        try:
            exec code in ns
        except Exception as e:
            self.warn('Error while processing setup: %s (%s)' % (full_path, str(e)))
            return None

        unique_id = 'setup-%s' % base_path.replace('.', '-').replace('/', '-')
        return {
                  'unique_id' : unique_id,
                  'setupname' : setup_name,
                  'basepath' : base_path,
                  'description': ns.get('description', setup_name),
                  'group': ns.get('group', 'optional'),
                  'sysconfig': ns.get('sysconfig', {}),
                  'includes': ns.get('includes', []),
                  'excludes': ns.get('excludes', []),
                  'modules': ns.get('modules', []),
                  'devices': ns.get('devices', {}),
                  'startupcode': ns.get('startupcode', ''),
                  'extended': ns.get('extended', {}),
                  }

    def _buildSetupRst(self, setup_info):
        setup_info['setupname_underline'] = '=' * len(setup_info['setupname'])

        setup_info['rst_group'] = self._buildGroupBlock(setup_info)
        setup_info['rst_includes'] = self._buildIncludesBlock(setup_info)
        setup_info['rst_excludes'] = self._buildExcludesBlock(setup_info)
        setup_info['rst_modules'] = self._buildModulesBlock(setup_info)
        setup_info['rst_devices'] = self._buildDevicesBlock(setup_info)
        setup_info['rst_startupcode'] = self._buildStartupcodeBlock(setup_info)

        return rstSnipSetup % setup_info

    def _buildGroupBlock(self, setup_info):
        return rstSnipGroup % setup_info if setup_info['group'] else ''

    def _buildIncludesBlock(self, setup_info):
        setup_info['includes'] = ', '.join(self._buildSetupLink(setup_info['basepath'], setup)
                                          for setup in setup_info['includes'])
        return rstSnipIncludes % setup_info if setup_info['includes'] else ''

    def _buildExcludesBlock(self, setup_info):
        setup_info['excludes'] = ', '.join(self._buildSetupLink(setup_info['basepath'], setup)
                                          for setup in setup_info['excludes'])
        return rstSnipExcludes % setup_info if setup_info['excludes'] else ''

    def _buildModulesBlock(self, setup_info):
        setup_info['modules'] = ', '.join(self._buildModuleLink(module)
                                         for module in setup_info['modules'])
        return rstSnipModules % setup_info if setup_info['modules'] else ''

    def _buildStartupcodeBlock(self, setup_info):
        if not setup_info['startupcode'].strip():
            return ''
        setup_info['startupcode'] = '\n    '.join(prepare_docstring(setup_info['startupcode']))
        return rstSnipStartupcode % setup_info

    def _buildDevicesBlock(self, setup_info):
        devices_dict = setup_info['devices']
        if not devices_dict:
            return ''

        rst = rstSnipDevices.split()
        rst.append('')

        for devName, (devClass, devParams) in sorted(devices_dict.items(),
                                                     key=lambda d: d[0].lower()):

            if not devClass.startswith('nicos.'):
                devClass = 'nicos.' + devClass

            klass = self._importDeviceClass(devClass)

            if not klass:
                continue

            rst.append('.. _%s-%s:\n' % (setup_info['unique_id'], devName))
            rst.append(devName)
            rst.append('~' * len(devName))
            rst.append('')
            rst.append('Device class: :class:`%s.%s`' % (klass.__module__, klass.__name__))
            rst.append('')

            if 'description' in devParams:
                rst.append(escape_rst(devParams['description']))
                rst.append('')

            paramRows = [('Parameter', 'Default', 'Configured')]

            for param_name in sorted(klass.parameters):
                param_info = klass.parameters[param_name]

                if not param_info.userparam or param_name in EXCLUDE_PARAMS:
                    continue

                if param_name in devParams:
                    paramValue = repr(devParams[param_name])
                    if len(paramValue) > 80:
                        paramValue = paramValue[:76] + ' ...'

                    paramRows += [(self._buildParamLink(param_name, param_info),
                                   escape_rst(repr(param_info.default)),
                                   escape_rst(paramValue))]
                else:
                    paramRows += [(self._buildParamLink(param_name, param_info),
                                   escape_rst(repr(param_info.default)), '')]

            rst.append(self._buildCSVTable(paramRows))
            rst.append('')

        return '\n'.join(rst)

    def _buildSetupLink(self, basepath, setup_name):
        setuplink = 'setup-%s-py' % path.join(path.dirname(basepath),
                                           setup_name).replace('/', '-')
        return rstSnipSetupLink % {
                                   'setupname' : setup_name,
                                   'setuplink' : setuplink
                                   }

    def _buildModuleLink(self, modulePath):
        return rstSnipModuleLink % {'modpath' : modulePath}

    def _buildParamLink(self, paramName, paramInfo):
        return rstSnipParamLink % {
                                   'classname' : paramInfo.classname,
                                   'paramname' : paramName
                                   }

    def _buildCSVTable(self, rows, indent_lvl=1, h_header=True, v_Header=True):
        rst = ['%s.. csv-table::' % (self.indention*indent_lvl)]
        rst.append('%s:widths: 20 25 55' % (self.indention*(indent_lvl + 1)))

        if h_header:
            rst.append('%s:header-rows: 1' % (self.indention*(indent_lvl + 1)))
        if v_Header:
            rst.append('%s:stub-columns: 1' % (self.indention*(indent_lvl + 1)))
        rst.append('')

        for row in rows:
            rst.append(self.indention*(indent_lvl + 1) +
                       ', '.join('"' + cell.replace('"', '""') + '"' for cell in row))
        rst.append('')
        return '\n'.join(rst)

    def _importDeviceClass(self, class_path):

        if class_path in devClassCache:
            return devClassCache[class_path]

        try:
            module, _, klass = class_path.rpartition('.')
            mod = __import__(module, None, None, ['*'])

            klass = getattr(mod, klass)
            devClassCache[class_path] = klass
            return klass
        except ImportError as e:
            self.warn('Could not import device class %s' % class_path)
        except AttributeError as e:
            self.warn(str(e))
            self.warn('Could not get device class %s from module' % class_path)
        return None


###############################################################################
##                                   Events                                  ##
###############################################################################

rstSnipSetupFile = '''
.. setup:: custom/%(custom)s/setups/%(setupname)s.py

'''


def _getListOfFiles(root, suffix):
    if not path.isdir(root):
        return set()

    result = []
    for entry in os.listdir(root):
        fullEntry = path.join(root, entry)
        if path.isdir(fullEntry):
            for subentry in os.listdir(path.join(root, entry)):
                if subentry.endswith(suffix):
                    result.append(path.join(entry, subentry)[:-len(suffix)])
        elif entry.endswith(suffix):
            result.append(entry[:-len(suffix)])

    return set(result)


def setupdoc_builder_inited(app):
    """Make sure there is a .rst file for each setup file in the custom section.

    .rst files that correspond to removed setups are removed.
    """
    base_dir = path.join(app.builder.srcdir,
                        app.config.setupdoc_setup_base_dir)
    cust_doc_dir = path.join(app.builder.srcdir,
                           app.config.setupdoc_custom_doc_dir)

    for custom in os.listdir(cust_doc_dir):
        if not path.isdir(path.join(cust_doc_dir, custom)):
            continue
        setup_dir = path.join(base_dir, 'custom', custom, 'setups')
        dest_dir = path.join(cust_doc_dir, custom, 'setups')
        setups = _getListOfFiles(setup_dir, '.py')
        rstfiles = _getListOfFiles(dest_dir, '.rst')

        added = setups - rstfiles
        deleted = rstfiles - setups

        for setup in deleted:
            os.unlink(path.join(dest_dir, setup + '.rst'))

        for setup in added:
            rstname = path.join(dest_dir, setup + '.rst')
            try:
                os.makedirs(path.dirname(rstname))
            except OSError:
                # ignore already existent dirs
                pass
            with open(rstname, 'w') as f:
                f.write(rstSnipSetupFile %
                        {'custom': custom, 'setupname': setup})


###############################################################################
##                                   Setup                                   ##
###############################################################################

def setup(app):
    app.add_config_value('setupdoc_setup_base_dir', '../..', '')
    app.add_config_value('setupdoc_custom_doc_dir', 'custom', '')

    app.add_directive('setup', SetupDirective)

    app.connect('builder-inited', setupdoc_builder_inited)
