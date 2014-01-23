# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
import os.path

from docutils import nodes
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.util.compat import Directive
from sphinx.util.docstrings import prepare_docstring

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
**Devices**

'''

rstSnipStartupcode = '''
**Startup code**

::

    %(startupcode)s
'''

rstSnipSetup = '''
.. _%(unique_id)s:

%(setupname)s
%(setupname_underline)s

*File: %(relsetuppath)s*

%(description)s

%(rst_group)s
%(rst_includes)s
%(rst_excludes)s
%(rst_modules)s

%(rst_devices)s

%(rst_startupcode)s
'''

devClassCache = {} # cache for already imported device classes


class SetupDirective(Directive):

    has_content = False
    required_arguments = 1
    base_path = os.path.abspath('..')
    indention = '    '

    def __init__(self, *args, **kwargs):
        Directive.__init__(self, *args, **kwargs)

        self.env = self.state.document.settings.env
        self.error = self.env.app.warn

    def run(self):
        return self._generateSetupNodes(self.arguments[0])

    def _generateSetupNodes(self, relPath):
        info = self._readSetup(relPath)

        if info:
            content = self._buildSetupRst(info)

            content = content.split('\n')
            content = ViewList(content, info['filename'])

            node = nodes.paragraph()
            nested_parse_with_titles(self.state, content, node)

            return node.children

        return []

    def _readSetup(self, relPath):
        self.info('Handle setup: %s' % relPath)

        # determine path
        path = os.path.join(self.base_path, relPath)

        if not path.endswith('.py'):
            self.error('Given setup is not a python file: %s' % relPath)
            return None

        setupName = os.path.basename(path)[:-3]

        try:
            with open(path, 'r') as modfile:
                code = modfile.read()
        except (ImportError, IOError) as e:
            self.error('Error while reading setup: %s (%s)' % (relPath, str(e)))
            return None

        ns = {
              'device': lambda cls, **params: (cls, params),
              'setupname' : setupName
              }

        try:
            exec code in ns
        except Exception as e:
            self.error('Error while processing setup: %s (%s)' % (relPath, str(e)))
            return None

        unique_id = 'setup-%s' % relPath.replace('.', '-').replace('/', '-')
        result = {
                  'unique_id' : unique_id,
                  'setupname' : setupName,
                  'relpath' : os.path.dirname(relPath),
                  'relsetuppath' : relPath,
                  'description': ns.get('description', setupName),
                  'group': ns.get('group', 'optional'),
                  'sysconfig': ns.get('sysconfig', {}),
                  'includes': ns.get('includes', []),
                  'excludes': ns.get('excludes', []),
                  'modules': ns.get('modules', []),
                  'devices': ns.get('devices', {}),
                  'startupcode': ns.get('startupcode', ''),
                  'extended': ns.get('extended', {}),
                  'filename': path,
                  }

        return result

    def _buildSetupRst(self, setupInfo):
        setupInfo['setupname_underline'] = '-' * len(setupInfo['setupname'])

        setupInfo['rst_group'] = self._buildGroupBlock(setupInfo)
        setupInfo['rst_includes'] = self._buildIncludesBlock(setupInfo)
        setupInfo['rst_excludes'] = self._buildExcludesBlock(setupInfo)
        setupInfo['rst_modules'] = self._buildModulesBlock(setupInfo)
        setupInfo['rst_devices'] = self._buildDevicesBlock(setupInfo)
        setupInfo['rst_startupcode'] = self._buildStartupcodeBlock(setupInfo)

        content = rstSnipSetup % setupInfo
        return content

    def _buildGroupBlock(self, setupInfo):
        rst = rstSnipGroup
        return rst % setupInfo if setupInfo['group'] else ''

    def _buildIncludesBlock(self, setupInfo):
        rst = rstSnipIncludes

        setupInfo['includes'] = ', '.join([self._buildSetupLink(setupInfo['relpath'], setup)
                                for setup in setupInfo['includes']])

        return rst % setupInfo if setupInfo['includes'] else ''

    def _buildExcludesBlock(self, setupInfo):
        rst = rstSnipExcludes

        setupInfo['excludes'] = ', '.join([self._buildSetupLink(setupInfo['relpath'], setup)
                                for setup in setupInfo['excludes']])

        return rst % setupInfo if setupInfo['excludes'] else ''

    def _buildModulesBlock(self, setupInfo):
        rst = rstSnipModules

        setupInfo['modules'] = ', '.join([self._buildModuleLink(module)
                                for module in setupInfo['modules']])

        return rst % setupInfo if setupInfo['modules'] else ''

    def _buildStartupcodeBlock(self, setupInfo):
        if not setupInfo['startupcode'].strip():
            return ''

        rst = rstSnipStartupcode

        setupInfo['modules'] = ', '.join([self._buildModuleLink(module)
                                for module in setupInfo['modules']])

        setupInfo['startupcode'] = '\n    '.join(prepare_docstring(setupInfo['startupcode']))

        return rst % setupInfo

    def _buildDevicesBlock(self, setupInfo):
        devicesDict = setupInfo['devices']
        if not devicesDict:
            return ''

        rst = rstSnipDevices.split()
        rst.append('')

        for devName, (devClass, devParams) in sorted(devicesDict.iteritems()):

            if not devClass.startswith('nicos.'):
                devClass = 'nicos.' + devClass

            klass = self._importDeviceClass(devClass)

            if not klass:
                continue

            rst.append('.. _%s-%s:\n' % (setupInfo['setupname'], devName))
            rst.append('%s| **%s (**\\ :class:`%s.%s`\\ **):**\n' % (self.indention, devName, klass.__module__, klass.__name__))

            if 'description' in devParams:
                rst.append('%s| %s' % (self.indention*2, devParams['description']))
                rst.append('')

            paramRows = [('Parameter', 'Default', 'Configured')]

            for paramName in sorted(klass.parameters.keys()):
                paramInfo = klass.parameters[paramName]

                if not paramInfo.userparam or paramName == 'description':
                    continue

                if paramName in devParams:
                    paramRows += [(self._buildParamLink(paramName, paramInfo), repr(paramInfo.default), repr(devParams[paramName]))]
                else:
                    paramRows += [(self._buildParamLink(paramName, paramInfo), repr(paramInfo.default), '')]

            rst.append(self._buildListTable(paramRows, 2))
            rst.append('')

        return '\n'.join(rst)

    def _buildSetupLink(self, relPath, setupName):
        setuplink = 'setup-%s-py' % os.path.join(relPath,
                                                 setupName).replace('/', '-')
        return rstSnipSetupLink % {
                                   'setupname' : setupName,
                                   'setuplink' : setuplink
                                   }

    def _buildModuleLink(self, modulePath):
        return rstSnipModuleLink % { 'modpath' : modulePath}

    def _buildParamLink(self, paramName, paramInfo):
        return rstSnipParamLink % {
                                   'classname' : paramInfo.classname,
                                   'paramname' : paramName
                                   }

    def _buildListTable(self, rows, indentionLevel=1, hHeader=True, vHeader=True):
        rst = ['%s.. list-table::' % (self.indention*indentionLevel)]
        rst.append('%s:widths: 20 25 55' % (self.indention*(indentionLevel + 1)))

        if hHeader:
            rst.append('%s:header-rows: 1' % (self.indention*(indentionLevel + 1)))
        if vHeader:
            rst.append('%s:stub-columns: 1' % (self.indention*(indentionLevel + 1)))
        rst.append('')

        for row in rows:
            for i in range(0, len(row)):
                rowRst = self.indention * (indentionLevel + 1)
                if not i:
                    rowRst += '*'
                else:
                    rowRst += ' '

                rowRst += ' - %s ' % str(row[i])
                rst.append(rowRst)

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
            self.error('Could not import %s' % classPath)
        except AttributeError as e:
            self.error(e)
            self.error('Could not get class from module %s' % classPath)
        return None

class SetupdirDirective(SetupDirective):
    def run(self):
        nodes = []

        relPath = self.arguments[0]
        path = os.path.join(self.base_path, relPath)
        path = os.path.abspath(path)

        if not os.path.isdir(path):
            self.error('Setup directory does not exist: %s' % path)
            return []


        for entry in sorted(os.listdir(path)): # explicitely NOT recursive!
            filePath = os.path.join(path, entry)

            if not os.path.isfile(filePath) \
                or not entry.endswith('.py') \
                or entry == '__init__.py':
                continue

            nodes += self._generateSetupNodes(os.path.join(relPath, entry))

        return nodes


def setup(app):
    app.add_directive('setup', SetupDirective)
    app.add_directive('setupdir', SetupdirDirective)
