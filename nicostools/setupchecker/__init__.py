# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

import ast
import logging
import os
import re
import traceback
from os import path

from nicos.clients.gui import config as guicfg
from nicos.clients.gui.config import prepareGuiNamespace
from nicos.core.device import DeviceAlias
from nicos.core.errors import ConfigurationError
from nicos.core.params import nicosdev_re
from nicos.core.sessions.setups import SETUP_GROUPS, fixup_stacked_devices, \
    prepareNamespace
from nicos.utils import checkSetupSpec, importString
from nicos.utils.files import findSetupRoots, iterSetups
from nicos.utils.loggers import StreamHandler

try:
    from nicos.clients.gui.panels import Panel
    from nicos.guisupport import qt
except ImportError:
    qt = None
    Panel = None

interpol_re = re.compile(
    r'%[-#0 +]*(?:[0-9]+)?(?:\.(?:[0-9]*))?'
    r'[hlL]?[diouxXeEfFgGcrs%]'
)


def setupname(filename):
    return path.basename(filename)[:-3]


class FileHandler(StreamHandler):

    def __init__(self, *args):
        StreamHandler.__init__(self, *args)
        self.setFormatter(
            logging.Formatter('! %(name)s: %(levelname)s: %(message)s')
        )


class Logger(logging.Logger):

    def handle(self, record):
        record.message = record.getMessage()
        record.filename = ''
        # the ColoredConsoleHandler does not use "line", make it part of name
        if getattr(record, 'line', 0):
            record.name = '%s:%s' % (record.name, record.line)
            record.line = ''
        logging.Logger.handle(self, record)


class SetupCollection:
    """Represents a bunch of setups that are available to a certain instrument
    configuration.
    """

    def __init__(self):
        self.log = logging.getLogger('collection')

        # results of collection
        self.all_setups = None      # All found setups with their paths.
        self.namespace = {}         # Setup file namespaces for each setup.
        self.setup_ast = {}         # Setup file ASTs.
        self.exec_errors = {}       # Errors during exec()ution of a setup.
        self.all_devs_lc = set()    # All devices seen, with lowercase name.

        # bookkeeping for SetupChecker
        self.devs_seen = {}
        self.helptopics_seen = {}

    def add(self, filename):
        if setupname(filename).startswith('guiconfig'):
            self._exec_all([(setupname(filename), filename)])
            return

        if self.all_setups is None:
            try:
                setup_roots = findSetupRoots(filename)
            except RuntimeError as err:
                self.log.error(str(err))
                setup_roots = (path.dirname(filename),)
            setuplist = list(iterSetups(setup_roots))
            self.all_setups = dict(setuplist)
            self._exec_all(setuplist)

    def _exec_all(self, setuplist):
        for (setupname, filename) in setuplist:
            self.log.info('excecuting %s', filename)
            filename = path.normpath(path.abspath(filename))
            is_guiconfig = setupname.startswith('guiconfig')
            if is_guiconfig:
                ns = prepareGuiNamespace()
            else:
                ns = prepareNamespace(setupname, filename, self.all_setups)
            try:
                with open(filename, encoding='utf-8') as fp:
                    code = fp.read()
                exec(code, ns)
            except SyntaxError as e:
                msg = 'SyntaxError:\t%s' % e.msg
                msg += '\n|line: %s : %s ' % (
                    e.lineno, e.text.strip() if e.text else ''
                )
                self.exec_errors[filename] = (e, msg)
            except Exception as e:
                self.exec_errors[filename] = (e, None)
            else:
                self.setup_ast[filename] = ast.parse(code)
                ns['devices'] = fixup_stacked_devices(self.log,
                                                      ns.get('devices', {}))
                self.namespace[filename] = ns

                for dev in ns.get('devices', {}):
                    self.all_devs_lc.add(dev.lower())


class SetupChecker:

    def __init__(self, collection, filename):
        self.log = logging.getLogger(filename)
        filename = path.normpath(path.abspath(filename))
        self.collection = collection
        self.filename = filename
        self.setupname = setupname(filename)
        if self.filename in self.collection.exec_errors:
            (exc, msg) = self.collection.exec_errors[self.filename]
            if msg:
                self.log_error(msg, extra={'line': exc.lineno})
            else:
                self.log_exception(exc)
            self.good = False
        else:
            self.ns = collection.namespace[filename]
            self.good = True

    def log_exception(self, exception):
        formatted_lines = traceback.format_exc().splitlines()
        msg = 'Exception while executing: %s\n|' % str(exception)
        msg += '\n|'.join(formatted_lines[-3:])
        self.log_error(msg)

    def log_error(self, msg, *args, **kw):
        self.good = False
        self.log.error(msg, *args, **kw)

    error = log_error  # disguise ourself as a logger object

    # find line numbers in the AST

    def _find_binding(self, binding):
        assign = [
            x for x in self.collection.setup_ast[self.filename].body
            if isinstance(x, ast.Assign) and isinstance(x.targets[0], ast.Name)
            and x.targets[0].id == binding
        ]
        if not assign:
            return None
        return assign[0]

    def find_global(self, binding):
        assign = self._find_binding(binding)
        if assign:
            return {'line': assign.lineno}
        return {'line': 0}

    def find_deventry(self, devname, parname=None):
        # find a binding for 'devices'
        assign = self._find_binding('devices')
        if not assign:
            return {'line': 0}
        dev_val = assign.value
        # now we look for the device() call that belongs to the given devname
        #
        # the 'devices' dict can be in two forms: either a dict literal
        if isinstance(dev_val, ast.Dict):
            # find index of the device we need in the keys
            for (i, key) in enumerate(dev_val.keys):
                if isinstance(key, ast.Str) and key.s == devname:
                    dev_call = dev_val.values[i]
                    break
                if isinstance(key, ast.BinOp):
                    try:
                        code = compile(
                            ast.fix_missing_locations(ast.Expression(key)),
                            '<string>', 'eval'
                        )
                        val = eval(code, self.ns)
                    except Exception:
                        self.log.error(
                            '%s: Error evaluating definition', ast.dump(key),
                            extra={'line': key.lineno}
                        )
                        continue
                    if val == devname:
                        dev_call = dev_val.values[i]
                        break
            else:
                # device not found
                return {'line': 0}
        # or a dict() call
        elif isinstance(dev_val, ast.Call) and dev_val.func.id == 'dict':
            # look for our device name in the kwargs
            for devkw in dev_val.keywords:
                if devkw.arg == devname:
                    dev_call = devkw.value
                    break
            else:
                # device not found
                return {'line': 0}
        # else it's something strange
        else:
            return {'line': 0}
        # we have our Call node in dev_call
        # do we need to look for param?
        if parname and isinstance(dev_call, ast.Call):
            for parkw in dev_call.keywords:
                if parkw.arg == parname:
                    return {'line': parkw.value.lineno}
        return {'line': dev_call.lineno}

    # check individual parameters

    def check_parameter(self, devname, name, value):
        # for format strings, check interpolations for syntax errors
        if name == 'fmtstr':
            if '%' not in value:
                self.log_error(
                    '%s: parameter fmtstr has a value without any '
                    'interpolation placeholders', devname,
                    extra=self.find_deventry(devname, name)
                )
                return False
            else:
                # split() returns all pieces not part of a string
                # interpolation placeholder, so they must not contain
                # any % signs
                pieces = interpol_re.split(value)
                for piece in pieces:
                    if '%' in piece:
                        self.log_error(
                            '%s: parameter fmtstr has an invalid '
                            'placeholder (%r)', devname, piece,
                            extra=self.find_deventry(devname, name)
                        )
                        return False
        return True

    def check_device(self, devname, devconfig, is_special=False):
        # check for valid name
        if not nicosdev_re.match(devname):
            self.log_error(
                '%s: device name is invalid (must be a valid '
                'Python identifier)' % devname,
                extra=self.find_deventry(devname)
            )
        # check for format of config entry
        if not isinstance(devconfig, tuple) or len(devconfig) != 2:
            self.log_error(
                '%s: device entry has wrong format (should be '
                'device() or a 2-entry tuple)' % devname,
                extra=self.find_deventry(devname)
            )
            return False
        # try to import the device class
        try:
            cls = importString(devconfig[0])
        except (ImportError, RuntimeError) as err:
            self.log.warning(
                'device class %r for %r not importable: %s', devconfig[0],
                devname, err, extra=self.find_deventry(devname)
            )
            return
        except Exception as e:
            self.log_error(
                'could not get device class %r for %r:', devconfig[0], devname,
                extra=self.find_deventry(devname)
            )
            return self.log_exception(e)
        config = devconfig[1].copy()

        # check missing attached devices
        if not hasattr(cls, 'attached_devices'):
            self.log.warning(
                "%s: class %r has no 'attached_devices'", devname, cls.__name__
            )
        else:
            for aname, ainfo in cls.attached_devices.items():
                try:
                    ainfo.check(None, aname, config.get(aname))
                except ConfigurationError as err:
                    self.log_error(
                        '%s: attached device %s (%s) is '
                        'wrongly configured: %s' %
                        (devname, aname, cls.__name__, err),
                        extra=self.find_deventry(devname, aname)
                    )
                if aname in config:
                    del config[aname]

        # check missing and unsupported parameter config entries
        if not hasattr(cls, 'parameters'):
            self.log.warning(
                "%s: class %r has no 'parameters'", devname, cls.__name__
            )
        else:
            if 'lowlevel' in config:
                self.log_error('%s: "lowlevel" parameter is given', devname,
                               extra=self.find_deventry(devname, 'lowlevel'))
            vis = config.get('visibility', cls.parameters['visibility'].default)
            if 'devlist' in vis and not issubclass(cls, DeviceAlias):
                if not config.get('description') and not is_special:
                    self.log.warning(
                        '%s: device has no description', devname,
                        extra=self.find_deventry(devname)
                    )
            for pname, pinfo in cls.parameters.items():
                if pname in config:
                    if pinfo.internal:
                        self.log_error(
                            "%s: '%s' is configured in a setup file although "
                            "declared as internal parameter", devname, pname,
                            extra=self.find_deventry(devname, pname)
                        )
                        del config[pname]
                        continue
                    try:
                        pinfo.type(config[pname])
                    except (ValueError, TypeError) as e:
                        self.log_error(
                            '%s: parameter %r value %r is '
                            'invalid: %s', devname, pname, config[pname], e,
                            extra=self.find_deventry(devname, pname)
                        )
                    # check value of certain parameters
                    self.check_parameter(devname, pname, config[pname])
                    del config[pname]
                elif pinfo.mandatory:
                    self.log_error(
                        '%s: mandatory parameter %r missing', devname, pname,
                        extra=self.find_deventry(devname)
                    )
        if config:
            onepar = list(config)[0]
            self.log_error(
                '%s: configured parameters not accepted by the '
                'device class: %s', devname, ', '.join(config),
                extra=self.find_deventry(devname, onepar)
            )

    def check(self):
        # report errors found by the collection phase
        if not self.good:
            return False

        # special check for guiconfigs
        if self.setupname.startswith('guiconfig'):
            return self.check_guiconfig()

        # check for valid group
        group = self.ns.get('group', 'optional')
        if group not in SETUP_GROUPS:
            self.log_error(
                'invalid setup group %r', group, extra=self.find_global('group')
            )

        if self.setupname in ('system', 'startup') and group != 'lowlevel':
            self.log.error("%s is not in 'lowlevel' setup group", self.filename)

        # check for a description
        description = self.ns.get('description', None)
        if description in (None, ''):
            self.log_error(
                'missing user-friendly setup description',
                extra=self.find_global('description')
            )

        devs = self.ns.get('devices', {})
        # check if devices are duplicated
        if group != 'special':
            for devname in devs:
                if devname not in self.collection.devs_seen:
                    self.collection.devs_seen[devname] = self.filename
                    continue
                # we have a duplicate: it's okay if we exclude the other setup
                # or if we are both basic setups
                other = self.collection.devs_seen[devname]
                self_group = self.ns.get('group', 'optional')
                other_group = self.collection.namespace[other].get('group',
                                                                   'optional')
                if self_group == 'basic' and other_group == 'basic':
                    continue
                if setupname(other) in self.ns.get('excludes', []) or \
                   self.setupname in self.collection.namespace[other].get(
                       'excludes', []):
                    continue
                # it's also ok if it is a sample, experiment, or instrument
                # device
                if devname in ['Sample', 'Exp'] or \
                   'instrument' in devs[devname][1]:
                    continue
                self.log.warning(
                    'device name %s duplicate: also in %s', devname,
                    self.collection.devs_seen[devname],
                    extra=self.find_deventry(devname)
                )
        # check for "require" or "requires"
        for req in ['require', 'requires']:
            if req in self.ns:
                self.log_error(
                    f"{req!r} should be substituted by 'includes'",
                    extra=self.find_global(req)
                )

        # check for common misspelling of "includes"
        if 'include' in self.ns:
            self.log_error(
                "'include' list should be called 'includes'",
                extra=self.find_global('include')
            )

        # check for common misspelling of "excludes"
        if 'exclude' in self.ns:
            self.log_error(
                "'exclude' list should be called 'excludes'",
                extra=self.find_global('exclude')
            )

        if os.path.basename(self.filename) == 'startup.py':
            if self.ns.get('includes', []):
                self.log_error(
                    "The 'includes' in 'startup.py' must be empty!",
                    extra=self.find_global('includes')
                )

        # check for types of recognized variables
        for (vname, vtype) in [
            ('description', str),
            # group is already checked against a fixed list
            ('sysconfig', dict),
            ('includes', list),
            ('excludes', list),
            ('modules', list),
            ('devices', dict),
            ('alias_config', dict),
            ('startupcode', str),
            ('display_order', int),
            ('extended', dict),
            ('watch_conditions', list),
            ('help_topics', dict),
        ]:
            if vname in self.ns and not isinstance(self.ns[vname], vtype):
                self.log_error(
                    '%r must be of type %s (but is %s)' %
                    (vname, vtype, type(self.ns[vname])),
                    extra=self.find_global(vname)
                )

        # check for importability of modules
        for module in self.ns.get('modules', []):
            # try to import the device class
            try:
                importString(module)
            except Exception as err:
                self.log_error(
                    'module %r not importable: %s', module, err,
                    extra=self.find_global('modules')
                )

        # check for validity of alias_config
        aliascfg = self.ns.get('alias_config', {})
        if isinstance(aliascfg, dict):  # else we complained above already
            for aliasname, entrydict in aliascfg.items():
                if not (isinstance(aliasname, str)
                        and isinstance(entrydict, dict)):
                    self.log_error(
                        'alias_config entries should map alias '
                        'device names to a dictionary',
                        extra=self.find_global('alias_config')
                    )
                    continue
                for target, prio in entrydict.items():
                    if not (isinstance(target, str)
                            and isinstance(prio, int)
                            and not isinstance(prio, bool)):
                        self.log_error(
                            'alias_config entries should map device '
                            'names to integer priorities',
                            extra=self.find_global('alias_config')
                        )
                        break
                    if target not in devs:
                        basedev = target.partition('.')[0]
                        if basedev not in devs:
                            self.log_error(
                                'alias_config device target should '
                                'be a device from the current setup',
                                extra=self.find_global('alias_config')
                            )
                            break

        # check for validity of display_order
        display_order = self.ns.get('display_order', 50)
        if not isinstance(display_order, int) or \
           not 0 <= display_order <= 100:
            self.log_error(
                'display_order should be an integer between '
                '0 and 100', extra=self.find_global('display_order')
            )

        # check for validity of extended representative
        representative = self.ns.get('extended', {}).get('representative')
        if representative is not None:
            if representative not in devs and representative not in aliascfg:
                self.log_error(
                    'extended["representative"] should be a device '
                    'defined in the current setup',
                    extra=self.find_global('extended')
                )

        # check for valid device classes (if importable) and parameters
        for devname, devconfig in devs.items():
            self.check_device(
                devname, devconfig, group in ('special', 'configdata')
            )

        # check if help topics are duplicated
        self.check_helptopics()

        # return overall "ok" flag
        return self.good

    def check_guiconfig(self):
        # special checks for guiconfig setups

        # check for main window
        if 'main_window' not in self.ns:
            self.log_error('main window spec is missing')
        else:
            self.check_guiconfig_panel_spec(self.ns['main_window'])

        for window in self.ns.get('windows', []):
            self.check_guiconfig_window_spec(window)

        for tool in self.ns.get('tools', []):
            self.check_guiconfig_tool_spec(tool)

        return self.good

    def check_guiconfig_panel_spec(self, spec, context='main window'):
        # recursively check a panel spec
        if isinstance(spec, (guicfg.hsplit, guicfg.vsplit, guicfg.hbox,
                             guicfg.vbox)):
            for child in spec.children:
                self.check_guiconfig_panel_spec(child, context)
        elif isinstance(spec, guicfg.tabbed):
            for child in spec.children:
                self.check_guiconfig_panel_spec(child[1], context)
        elif isinstance(spec, guicfg.docked):
            self.check_guiconfig_panel_spec(spec[0])
            for child in spec[1]:
                if not (isinstance(child, tuple) and len(child) == 2):
                    self.log_error(
                        'dock item should be a (name, panel) tuple,'
                        ' found %r', child
                    )
                else:
                    self.check_guiconfig_panel_spec(child[1], context)
        elif isinstance(spec, guicfg.panel):
            try:
                cls = importString(spec.clsname)
            except Exception as err:
                self.log_error(
                    'class %r for %s not importable: %s', spec.clsname, context,
                    err
                )
            else:
                if qt and not issubclass(cls, Panel):
                    self.log.warning(
                        'class %r for %s is not a Panel '
                        'subclass', spec.clsname, context
                    )
            self.validate_setup_spec(spec)
        else:
            self.log_error('found unsupported panel item %r', spec)

    def check_guiconfig_window_spec(self, spec):
        # recursively check a window spec
        if not isinstance(spec, guicfg.window):
            self.log_error('window spec %r is not a window()', spec)

        self.check_guiconfig_panel_spec(spec.contents, 'window %s' % spec.name)
        self.validate_setup_spec(spec)

    def check_guiconfig_tool_spec(self, spec):
        # recursively check a tool spec
        if not isinstance(spec, (guicfg.tool, guicfg.cmdtool, guicfg.menu)):
            self.log_error('tool spec %r is not a tool() or cmdtool()', spec)

        if isinstance(spec, guicfg.menu):
            for tool in spec.items:
                self.check_guiconfig_tool_spec(tool)

        if isinstance(spec, guicfg.tool):
            try:
                cls = importString(spec.clsname)
            except Exception as err:
                self.log_error(
                    'class %r for tool %r not importable: %s', spec.clsname,
                    spec.name, err
                )
            else:
                if qt and not issubclass(cls, (qt.QDialog, qt.QMainWindow)):
                    self.log.warning(
                        'class %r for tool %r is not a QDialog or'
                        ' QMainWindow', spec.clsname, spec.name
                    )
            self.validate_setup_spec(spec)

    def check_helptopics(self):
        group = self.ns.get('group', 'optional')
        if group != 'special':
            helptopics = self.ns.get('help_topics', {})
            for helpname in helptopics:
                if helpname not in self.collection.helptopics_seen:
                    self.collection.helptopics_seen[helpname] = self.filename
                    continue
                other = self.collection.helptopics_seen[helpname]
                self_group = self.ns.get('group', 'optional')
                other_group = self.collection.namespace[other].get('group',
                                                                   'optional')
                if self_group == 'basic' and other_group == 'basic':
                    continue
                if setupname(other) in self.ns.get('excludes', []) or \
                   self.setupname in self.collection.namespace[other].get(
                       'excludes', []):
                    continue
                self.log.error(
                    'Help topic name %s duplicate: also in %s', helpname,
                    self.collection.helptopics_seen[helpname]
                )
        return self.good

    def validate_setup_spec(self, spec):
        """Validate the 'setups' option.

        If there is a definitions of the old style of setup dependenciest a
        warning will be given.
        """
        setupspec = spec.options.get('setups', '')
        checkSetupSpec(setupspec, '', log=self.log)


class SetupValidator:
    def walk(self, paths, separate=False):
        good = True
        collection = SetupCollection()
        for p in paths:
            if separate:
                collection = SetupCollection()
            if path.isdir(p):
                self.collectRecursive(collection, p)
                self.validateRecursive(collection, p)
            elif path.isfile(p):
                collection.add(p)
                good &= SetupChecker(collection, p).check()
            if not path.exists(p):
                # Explicitly no negative return value as the rest of the paths
                # may have been checked.
                log = logging.getLogger(p)
                log.error('File not found')
        return good

    def collectRecursive(self, c, p):
        for root, _dirs, files in os.walk(p):
            for f in files:
                if f.endswith('.py'):
                    c.add(path.join(root, f))

    def validateRecursive(self, c, p):
        good = True
        for root, _dirs, files in os.walk(p):
            for f in files:
                if f.endswith('.py'):
                    good &= SetupChecker(c, path.join(root, f)).check()
        return good
