#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
from docutils.parsers.rst import Directive
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.util.docstrings import prepare_docstring

from nicos.core.sessions.setups import readSetup

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
.. _%(uniqueid)s:

%(setupname)s
%(setupname_underline)s

*File: %(shortsetuppath)s*

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
        # simplify env access
        self.env = self.state.document.settings.env

        # short setup path:
        # like it's used in nicos (setup_pkg/instr/setups/setup.py)
        self._shortSetupPath = self.arguments[0]
        self._absSetupPath = self._getAbsoluteSetupPath(self._shortSetupPath)
        self._setupName = path.basename(self._absSetupPath)[:-3]

        ## relative to the doc source dir
        #rel_path = path.join(self.env.config.setupdoc_setup_base_dir,
        #                     self.arguments[0])

        # note actual setup as dependency
        self.env.note_dependency(self._absSetupPath)

        info = self._readSetup()
        node = nodes.paragraph()
        if info:
            content = self._buildSetupRst(info)
            content = ViewList(content.splitlines(), self._absSetupPath)
            nested_parse_with_titles(self.state, content, node)

        return node.children

    def exception(self, *args, **kwargs):
        self.warn(*args, **kwargs)

    def warn(self, *args, **kwargs):
        self.env.app.warn(*args, **kwargs)

    def _readSetup(self):
        uniqueId = self._getUniqueSetupId(self._shortSetupPath)

        setups = {}
        readSetup(setups, self._absSetupPath, self)

        if not setups:
            # logging will be done by readSetup
            return None

        info = setups.values()[0]
        info['uniqueid'] = uniqueId
        info['setupname'] = self._setupName
        info['shortsetuppath'] = self._shortSetupPath

        return info

    def _buildSetupRst(self, setupInfo):
        setupInfo['setupname_underline'] = '=' * len(setupInfo['setupname'])

        setupInfo['rst_group'] = self._buildGroupBlock(setupInfo)
        setupInfo['rst_includes'] = self._buildIncludesBlock(setupInfo)
        setupInfo['rst_excludes'] = self._buildExcludesBlock(setupInfo)
        setupInfo['rst_modules'] = self._buildModulesBlock(setupInfo)
        setupInfo['rst_devices'] = self._buildDevicesBlock(setupInfo)
        setupInfo['rst_startupcode'] = self._buildStartupcodeBlock(setupInfo)

        return rstSnipSetup % setupInfo

    def _buildGroupBlock(self, setupInfo):
        return rstSnipGroup % setupInfo if setupInfo['group'] else ''

    def _buildIncludesBlock(self, setupInfo):
        setupInfo['includes'] = ', '.join(self._buildSetupLink(setup)
                                          for setup in setupInfo['includes'])
        return rstSnipIncludes % setupInfo if setupInfo['includes'] else ''

    def _buildExcludesBlock(self, setupInfo):
        setupInfo['excludes'] = ', '.join(self._buildSetupLink( setup)
                                          for setup in setupInfo['excludes'])
        return rstSnipExcludes % setupInfo if setupInfo['excludes'] else ''

    def _buildModulesBlock(self, setupInfo):
        setupInfo['modules'] = ', '.join(self._buildModuleLink(module)
                                         for module in setupInfo['modules'])
        return rstSnipModules % setupInfo if setupInfo['modules'] else ''

    def _buildStartupcodeBlock(self, setupInfo):
        if not setupInfo['startupcode'].strip():
            return ''
        setupInfo['startupcode'] = '\n    '.join(prepare_docstring(setupInfo['startupcode']))
        return rstSnipStartupcode % setupInfo

    def _buildDevicesBlock(self, setupInfo):
        devices_dict = setupInfo['devices']
        if not devices_dict:
            return ''

        rst = rstSnipDevices.split()
        rst.append('')

        for devName, (devClass, devParams) in sorted(devices_dict.items(),
                                                     key=lambda d: d[0].lower()):

            # Try to find classname with nicos prefix
            # TODO: This should be removed once we transitioned to full path
            # specs everywhere
            if not (devClass.startswith('nicos.') or
                    devClass.startswith('nicos_mlz.')):
                devClass = 'nicos.' + devClass

            klass = self._importDeviceClass(devClass)

            if not klass:
                continue

            rst.append('.. _%s-%s:\n' % (setupInfo['uniqueid'], devName))
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

    def _buildSetupLink(self, setup_name):
        shortPath = '%s.py' % path.join(path.dirname(self._shortSetupPath),
                                        setup_name)
        fullPath = self._getAbsoluteSetupPath(shortPath)

        if path.exists(fullPath):
            setuplink = self._getUniqueSetupId(shortPath)
            return rstSnipSetupLink % {
                                       'setupname' : setup_name,
                                       'setuplink' : setuplink
                                       }
        return setup_name

    def _buildModuleLink(self, modulePath):
        return rstSnipModuleLink % {'modpath' : modulePath}

    def _buildParamLink(self, paramName, paramInfo):
        return rstSnipParamLink % {
                                   'classname' : paramInfo.classname,
                                   'paramname' : paramName
                                   }

    def _buildCSVTable(self, rows, indent_lvl=1, hHeader=True, vHeader=True):
        rst = ['%s.. csv-table::' % (self.indention*indent_lvl)]
        rst.append('%s:widths: 20 25 55' % (self.indention*(indent_lvl + 1)))

        if hHeader:
            rst.append('%s:header-rows: 1' % (self.indention*(indent_lvl + 1)))
        if vHeader:
            rst.append('%s:stub-columns: 1' % (self.indention*(indent_lvl + 1)))
        rst.append('')

        for row in rows:
            rst.append(self.indention*(indent_lvl + 1) +
                       ', '.join('"' + cell.replace('"', '""') + '"' for cell in row))
        rst.append('')
        return '\n'.join(rst)

    def _importDeviceClass(self, classPath):

        if classPath in devClassCache:
            return devClassCache[classPath]

        try:
            module, _, klass = classPath.rpartition('.')
            mod = __import__(module, None, None, ['*'])

            klass = getattr(mod, klass)
            devClassCache[classPath] = klass
            return klass
        except ImportError as e:
            self.warn('Could not import device class %s' % classPath)
        except AttributeError as e:
            self.warn(str(e))
            self.warn('Could not get device class %s from module' % classPath)
        return None

    def _getAbsoluteSetupPath(self, shortPath):
        '''
        Return the absolute path to the setup file.
        short path is: setup_pkg/xy/setups/z.py
        '''
        return path.join(self.env.srcdir,
                        self.env.config.setupdoc_setup_base_dir,
                        shortPath)

    def _getUniqueSetupId(self, shortPath):
        return 'setup-%s' % shortPath.replace('.', '-').replace('/', '-')



###############################################################################
##                                   Events                                  ##
###############################################################################

rstSnipSetupFile = '''
.. setup:: nicos_mlz/%(custom)s/setups/%(setupname)s.py

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
        setup_dir = path.join(base_dir, 'nicos_mlz', custom, 'setups')
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
    app.add_config_value('setupdoc_custom_doc_dir', 'nicos_mlz', '')

    app.add_directive('setup', SetupDirective)

    app.connect('builder-inited', setupdoc_builder_inited)
    return {'parallel_read_safe': True,
            'version': '0.1.0'}
