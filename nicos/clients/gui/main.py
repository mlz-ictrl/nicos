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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS GUI application startup."""

from __future__ import print_function

import sys
import logging
import traceback
import argparse
from os import path

from PyQt4.QtGui import QApplication

from nicos import config
from nicos.utils import parseConnectionString
from nicos.utils.loggers import ColoredConsoleHandler, NicosLogfileHandler, \
    NicosLogger, initLoggers
from nicos.clients.base import ConnectionData
from nicos.clients.gui.mainwindow import MainWindow
from nicos.clients.gui.utils import SettingGroup, DebugHandler
from nicos.clients.gui.config import gui_config, prepareGuiNamespace
from nicos.clients.gui.dialogs.instr_select import InstrSelectDialog
from nicos.protocols.daemon import DEFAULT_PORT
from nicos.pycompat import exec_


log = None


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file', dest='configfile', default=None,
                        help='use the configuration file CONFIGFILE')
    parser.add_argument('-v', '--view-only', dest='viewonly', default=False,
                        action='store_true', help='Run in view-only mode')
    parser.add_argument('connect', nargs='?', default=None,
                        help='''A connection string with the following form:

                        [user_name[:password[@host[:port]]]]''')
    return parser.parse_args()


def main(argv):
    global log  # pylint: disable=global-statement

    # Import the compiled resource file to register resources
    import nicos.guisupport.gui_rc  # pylint: disable=unused-import, unused-variable

    userpath = path.join(path.expanduser('~'), '.config', 'nicos')

    # Set up logging for the GUI instance.
    initLoggers()
    log = NicosLogger('gui')
    log.parent = None
    log.setLevel(logging.INFO)
    log.addHandler(ColoredConsoleHandler())
    log.addHandler(NicosLogfileHandler(path.join(userpath, 'log'), 'gui',
                                       use_subdir=False))

    # set up logging for unhandled exceptions in Qt callbacks
    def log_unhandled(*exc_info):
        traceback.print_exception(*exc_info)  # pylint: disable=no-value-for-parameter
        log.exception('unhandled exception in QT callback', exc_info=exc_info)
    sys.excepthook = log_unhandled

    app = QApplication(argv, organizationName='nicos', applicationName='gui')

    opts = parseargs()

    if opts.configfile is None:
        try:
            config.apply()
        except RuntimeError:
            pass
        # If started from nicos-demo, we get an explicit guiconfig.  Therefore,
        # if "demo" is detected automatically, let the user choose.
        if (config.setup_package == 'nicos_demo'
                and config.instrument == 'demo') or config.instrument is None:
            configfile = InstrSelectDialog.select('Your instrument could not '
                                                  'be automatically detected.')
            if configfile is None:
                return
        else:
            configfile = path.join(config.setup_package_path, config.instrument,
                                   'guiconfig.py')

    with open(configfile, 'rb') as fp:
        configcode = fp.read()

    ns = prepareGuiNamespace()
    exec_(configcode, ns)
    gui_conf = gui_config(ns['main_window'], ns.get('windows', []),
                          ns.get('tools', []), ns.get('name', 'NICOS'),
                          ns.get('options', {}))
    if gui_conf.name != 'NICOS':
        SettingGroup.global_group = gui_conf.name

    stylefiles = [
        path.join(userpath, 'style-%s.qss' % sys.platform),
        path.join(userpath, 'style.qss'),
        path.splitext(configfile)[0] + '-%s.qss' % sys.platform,
        path.splitext(configfile)[0] + '.qss',
    ]
    for stylefile in stylefiles:
        if path.isfile(stylefile):
            try:
                with open(stylefile, 'r') as fd:
                    app.setStyleSheet(fd.read())
                break
            except Exception:
                log.warning('Error setting user style sheet from %s',
                            stylefile, exc=1)

    mainwindow = MainWindow(log, gui_conf)
    log.addHandler(DebugHandler(mainwindow))

    if opts.connect:
        parsed = parseConnectionString(opts.connect, DEFAULT_PORT)
        if parsed:
            cdata = ConnectionData(**parsed)
            cdata.viewonly = opts.viewonly
            mainwindow.setConnData(cdata)
            if cdata.password is not None:
                # we have a password, connect right away
                mainwindow.client.connect(mainwindow.conndata)
            else:
                # we need to ask for password, override last preset (uses given
                # connection data) and force showing connect window
                mainwindow.lastpreset = ''
                mainwindow.autoconnect = True
    mainwindow.startup()

    return app.exec_()
