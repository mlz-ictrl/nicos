#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
#
# *****************************************************************************

"""The NICOS electronic logbook."""

__version__ = "$Revision$"

from os import path
from cgi import escape

from nicos.elog.utils import formatMessage

try:
    import creole
except ImportError:
    creole = None

PROLOG = '''\
<html>
<head>
<style type="text/css">
body      { font-family: 'Arial', 'Helvetica', sans-serif; }
.remark   { font-weight: bold; }
.sample   { font-weight: bold; }
.msgblock { cursor: pointer; }
.messages { display: none; margin-left: 20px; border: 1px solid #ccc;
            background-color: #eee; }
.messages .debug { color: #666; }
.messages .input { font-weight: bold; }
.messages .warn  { color: #c000c0; }
.messages .err   { font-weight: bold; color: #c00000; }
</style>
<script type="text/javascript">
function hideshow(divel) {
  var el = divel.childNodes[1];
  if (el.style.display == 'block') {
    el.style.display = 'none';
  } else {
    el.style.display = 'block';
  }
}
</script>
<title>NICOS electronic logbook</title>
</head>
<body>
'''


class HtmlWriter(object):
    def __init__(self):
        self.fd = None
        self.curstate = None
        self.statesuffix = None

    def open(self, filename):
        if self.fd:
            self.endstate()
            self.fd.close()
        exists = path.isfile(filename) and path.getsize(filename)
        self.fd = open(filename, 'ab')
        if not exists:
            self.emit(PROLOG)

    def emit(self, html):
        if self.fd:
            self.fd.write(html)
            self.fd.flush()

    def newstate(self, state, prefix, suffix, html):
        if state != self.curstate:
            self.endstate()
            self.statesuffix = suffix
            self.curstate = state
            self.emit(prefix)
        self.emit(html)

    def endstate(self):
        if self.curstate:
            self.emit(self.statesuffix)
            self.curstate = None


class Handler(object):
    def __init__(self, log):
        self.log = log
        self.handlers = {}
        # register all handlers
        for name, func in Handler.__dict__.iteritems():
            if name.startswith('handle_'):
                self.handlers[name[7:].replace('_', '/')] = getattr(self, name)

        self.dir = None
        self.out = HtmlWriter()

    def handle_directory(self, dir):
        self.dir = dir
        self.out.open(path.join(dir, 'logbook.html'))
        self.log.info('Openend new output file in ' + dir)

    def handle_newexperiment(self, data):
        proposal, title = data
        self.out.emit('<h1>Experiment %s: %s</h1>\n' % (proposal, title))

    def handle_setup(self, setupnames):
        self.out.newstate('plain', '', '',
            '<p class="setup">New setup: %s</p>\n' % setupnames)

    def handle_entry(self, data):
        if creole:
            data = creole.translate(data)
        else:
            data = escape(data)
        self.out.newstate('entry', '', '', data)

    def handle_remark(self, remark):
        self.out.newstate('plain', '', '',
            '<p class="remark">%s</p>\n' % escape(remark))

    def handle_sample(self, data):
        self.out.newstate('plain', '', '',
            '<p class="sample">New sample: %s</p>\n' % escape(data))

    def handle_attachment(self, data):
        print 'XXX Attachment:', data

    def handle_message(self, message):
        msg = formatMessage(message)
        if msg:
            self.out.newstate('messages',
                '<div class="msgblock" onclick="hideshow(this)">Messages'
                '<pre class="messages">\n', '</pre></div>\n', msg)

    def handle_scanbegin(self, dataset):
        print 'XXX Scan begin:', dataset

    def handle_scanend(self, dataset):
        print 'XXX Scan end:', dataset


# XXX more ideas:
# - internal links -> reference scan numbers or attachments
# - integrated latex $foo$ syntax
# - count()s
# - show errors in messages (or at least summary: "1 error")
