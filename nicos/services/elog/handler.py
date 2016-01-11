#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

import io
from os import path, unlink
from cgi import escape
from time import strftime, localtime
from shutil import copyfile
from logging import ERROR

from nicos.services.elog.utils import formatMessage, pretty1, pretty2
from nicos.services.elog.genplot import plotDataset
from nicos.pycompat import to_utf8

try:
    import nicos._vendor.creole as creole
except ImportError:
    creole = None

FRAMESET = u'''\
<html>
<head>
<title>%s logbook: %s</title>
</head>
<frameset cols="200,*">
<frame src="toc.html">
<frame src="content.html" name="content">
</frameset>
</html>
'''

PROLOG = b'''\
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<style type="text/css">
.attach:before  { content: url('data:image/png;base64,\
iVBORw0KGgoAAAANSUhEUgAAABEAAAAQCAYAAADwMZRfAAAAAXNSR0IArs4c6QAAAAZiS0dEAP8A\
/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9wDGQ8LEDaGmqMAAAFZSURBVDjL\
jdMxSJVRGMbxnyAJhlKDIok0CSZNLeFiSoQQ0iZNEQ01hFtDW4PS0pBig6g4NHhpVtoEF6G7CLUU\
BS25BLW4eAOz2/IIB/nu5R744Lznfd8/zznv89HZGsd7NPP9xQIuddjvKU7wB8/wBG8C+9IJaC7F\
39EfRXcwhNnkXrQDPErRR/RgrbjOb4xgFY1WgHspPsRlvEq8ESXNqHyQfeUVTvEVvVhO4WLxRk3c\
xuMqyEwOf2IgE2jibfLTiQ/Qnbp6CbibKfxAH16mYSn5+/iHPVzAdvKTZ4BbxYMNYD7xu+QnEn/G\
Rawnrp0BruAo0oYLcy1nPxuF9SioBfC6vMbzHF6reOQb53yyknjnfOEmvlUApuLST/HJRgDrVSNd\
idxyXW/hk91WxrpZjO1hoI2o6yt8soWudhZfxK+M8BgfMIixAPY7/VsHMYqrxVlXxt/drvE/nU9k\
avdp7V4AAAAASUVORK5CYII='); margin-right: 10px; }
.scriptbegin:before { content: url('data:image/png;base64,\
iVBORw0KGgoAAAANSUhEUgAAABIAAAAQCAYAAAAbBi9cAAAAAXNSR0IArs4c6QAAAAZiS0dEAP8A\
/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9wDGQ8NHodkECIAAAElSURBVDjL\
ndS7SgNRFIXhL4l4IWJsrMROEHwAIZXY2Sg2IuIrKGJnIxY+gfgKijZaWHgDrRQ7C28oiIK1xNiZ\
QsfmBOJkJgnZcNjMYZ2fNevsmZz2qxO7GMNlR5uQLkxhNjz/VEGrmEe2weHecPAGp7jHAnYwAsuI\
UMZnyipjIwAvgj7CFuaQh2/stfA6OZwFwG/od+irCiKsNYFkcBSD3GKgVhRhvQnoOAZ5QKFWkG0C\
6MEhJgMggydM4ysuTnPUjYOYk2cMoW5sGjkaxntNRi8oYjQp0zRQIdzIK/bxhhmUcBLc/au0yV4J\
fRPj+MBjLI6WHC3iHBO4jkESq+ooH9sfRCVlKIXw60DbWApfc6VGmOS2GPpVkqv+8DuIWlilEHpd\
/QHNJVMPjyyp4QAAAABJRU5ErkJggg=='); margin-right: 10px; }
.sample:before { content: url('data:image/png;base64,\
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAAZiS0dEAP8A\
/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9wDGQ8SFKrr96IAAACcSURBVDjL\
nZLNDYMwDIW/DlOuvaN2ECTO7RSZhBmYgwszdAZ+LkVIpJdGQpFrG56US+Ln98nxBeiRNQBP4I2h\
qJwZKLwNWqACxt3dBkzA1dMg6SWQTBpJKmqA2w87b6CSpILcEL0kqzFIk6QyUl0k4YD5L0l9gqTL\
5xGc6RH4AA/pV7wkd225gpK8WGaLxGWWSJaj5v2erEApPX4BzWqNI+7tFigAAAAASUVORK5CYII=\
'); margin-right: 10px; }
.setup:before { content: url('data:image/png;base64,\
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAAZiS0dEAP8A\
/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9wDGQ8UFPyxUCQAAAEaSURBVDjL\
ndI/L0RBFAXw365SaCj0OsLqSDQaYSMajUqlo/NFNL6ARK3Q0UhEs9GuikIkolBYf0Kw9mnuY/Ls\
k42T3Mxk7rnnnpm5FT+YQD+ucYMRTOIWTT1gF228I4v1E4d/FfWhhi3MYyjO8lwl1nE84aqbyDI6\
0bWDM2zgNBxkEZtlLgbxFqRGIXeQCIyGo1/Iklgv5FYTZ1mZg2l8BOGkkNtLxGtlAlMh0InYRz2K\
20n3tTKB2eh8n5CzxPozjrCIGayUCe0UCvP9EbZjmPLzJo6LAvX4vrEgzYXthXCY4TEiw0WZk0qX\
OcniKjkews1steRbU7S6cF6j0bAe0QjhVnTP30G1R4EXnMfUDuASd/6BpXjcb3wBMQZeIkiUnJMA\
AAAASUVORK5CYII='); margin-right: 10px; }
.environment:before { content: url('data:image/png;base64,\
iVBORw0KGgoAAAANSUhEUgAAAA8AAAAQCAYAAADJViUEAAAAAXNSR0IArs4c6QAAAAZiS0dEAP8A\
/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9wDGQ8jJT1o8CoAAAC/SURBVCjP\
pZExCsJQDIa/tiKCi1uhJ+gFnBzFwSt0dGgHL9KLOdXZHqCDF+ggIq1LCs+YoGggPPjzfyHJg9dI\
gSPQAmOQregpTpTANQAG9Y5SLzVYGEYrp3oxgSug+wDp7ISjMrr3wAHYytsbU1UAjRLvQKbWykQP\
fSeMjrVz0Fr5HjEQKdPZgbWeYBwjd+Bce2PDNDjwm27BiQN7+m8RARs1SQPcDO8CWIfjz4BdYJgD\
FwdeAnv5b3fnr+Mv+AkLPVjDfYckaQAAAABJRU5ErkJggg=='); margin-right: 10px; }
.detectors:before { content: url('data:image/png;base64,\
iVBORw0KGgoAAAANSUhEUgAAABkAAAAOCAYAAADaOrdAAAAAAXNSR0IArs4c6QAAAAZiS0dEAP8A\
/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9wDGQ8lEtOP8qMAAAGZSURBVDjL\
ldQ7aFVBEAbgLz4K8YlgJCgIQcRCVAKaVlCwUbDTTgS7YGejldiIjQ80CsF0QWyiEotY2FiIKCgW\
CpIiiqAQjaKpDNfca/MfWC73JDcDyzkzszv/PzM722NxWY012I1BbEcTLXzGU/zEPP5ZpqzCQVzH\
rwStWx9wOUS6lm0Ywe8iULMGoLR/DdiSsi9lqAve7ML+CmvrAE5hrsPBGziHv22Bp3EajzoAv8e6\
doAD+FJsns3/6/gf1zAfir8VEjOF7xk2VwCbkmIrfbiFY8lqGCsKAu3rYWJM4U1u4G38if9uLpEr\
MSzgaA4NhNlE9JcYT7Ayk0vxN0J0a/TD+JQ9A1Wzq8NjxQ17F9sGnEkpyp7NYy+ORH9QlH84tgls\
rIx70shWAHfhXvTx7DmfMjTwHSdin03WZ7GjIDyJ3vbm9+FJgjQwWgziHazP9PenT/14Hv83XM3/\
HG6iZ7FZGcLHDk2eCtiFlHWm8C3k+wLHu536nbiIH0s8KdV6i5PYstz3a2Um9xDu59komU/jGvan\
jLXyH3Wauf0/mhjGAAAAAElFTkSuQmCC'); margin-right: 10px; }
body      { font-family: 'Lucida Grande', 'Helvetica', 'Arial', sans-serif; }
pre, tt   { font-family: 'Dejavu Sans Mono', 'Bitstream Vera Sans Mono',
                         'Consolas', 'Menlo', monospace; }
.remark   { font-weight: bold; }
.sample   { font-weight: bold; }
.script   { font-weight: bold; }
.time     { font-size: small; float: right; background-color: #eee; }
.msgblock { cursor: pointer; margin-left: 20px; }
.msglabel { font-size: small; border: 1px solid #ccc;
            background-color: #eee; }
.messages { display: none; margin: 0; border: 1px solid #ccc;
            background-color: #eee; font-size: 10pt; }
.messages .debug { color: #666; }
.messages .input { font-weight: bold; }
.messages .warn  { color: #c000c0; }
.messages .err   { font-weight: bold; color: #c00000; }
.errblock .messages { display: block; }
ul.toc        { padding-left: 20px; list-style-type: square;
                font-size: 90%; }
body > ul.toc { padding-left: 0; }
ul.toc li     { margin-bottom: 0.5em; }
a             { text-decoration: none; color: #03c; }
a:hover       { text-decoration: underline; color: #05f; }
table         { border-collapse: collapse; }
td, th        { border: 1px solid #ccc; padding: 3px; }
th            { text-align: left; }
.scan         { width: 100%; }
.scannum      { font-weight: bold; }
.showlinks    { font-size: small; }
.contenthead  { letter-spacing: 0.15em; }
</style>
<script type="text/javascript">
function hideshow(divel) {
  var pre = divel.childNodes[1];
  var span = divel.childNodes[0];
  if (pre.style.display == 'block') {
    pre.style.display = 'none';
    span.style.display = 'inline';
  } else {
    pre.style.display = 'block';
    span.style.display = 'none';
  }
}
function msgshow() {
  var els = document.getElementsByClassName('msgblock');
  for (var i = 0; i < els.length; i++) {
    els[i].childNodes[0].style.display = 'none';
    els[i].childNodes[1].style.display = 'block';
  }
}
function msghide() {
  var els = document.getElementsByClassName('msgblock');
  for (var i = 0; i < els.length; i++) {
    els[i].childNodes[0].style.display = 'inline';
    els[i].childNodes[1].style.display = 'none';
  }
}
</script>
<title>NICOS electronic logbook</title>
</head>
<body>
'''

PROLOG_TOC = b'''\
<p class="showlinks">
  <a href="javascript:parent.content.msgshow()">Show all messages</a><br>
  <a href="javascript:parent.content.msghide()">Hide all messages</a>
</p>
<p class="contenthead">Contents</p>
'''


class HtmlWriter(object):
    def __init__(self):
        self.fd = None
        self.curstate = None
        self.statesuffix = None
        self.fd_toc = None
        self.toc_level = 0
        self.curid = 0
        self.idstart = strftime('%Y%m%d%H%M%S')

    def close(self):
        if self.fd:
            self.endstate()
            self.fd.close()
            self.fd_toc.write(b'</ul>' * self.toc_level)
            self.fd_toc.close()
        self.toc_level = 0

    def create_or_open(self, filename):
        if not path.isfile(filename):
            io.open(filename, 'wb').close()
        # we have to open in binary mode since we want to seek from the end,
        # which the text wrapper doesn't support
        return io.open(filename, 'r+b')

    def open(self, directory, instr, proposal):
        self.close()
        io.open(path.join(directory, 'logbook.html'), 'w').write(
            FRAMESET % (instr, proposal))
        self.fd = self.create_or_open(path.join(directory, 'content.html'))
        self.fd.seek(0, 2)
        if self.fd.tell() == 0:
            self.fd.write(PROLOG)
            self.fd.flush()
        self.fd_toc = self.create_or_open(path.join(directory, 'toc.html'))
        self.fd_toc.seek(0, 2)
        if self.fd_toc.tell() == 0:
            self.fd_toc.write(PROLOG + PROLOG_TOC)
            self.fd_toc.flush()

    def emit(self, html, suffix=u''):
        html = to_utf8(html)
        suffix = to_utf8(suffix)
        if self.fd:
            self.fd.write(html)
            # write suffix now, but place file pointer so that it's overwritten
            # on subsequent writes in the same state -- this way we can
            # guarantee that tags don't stay open
            if suffix:
                self.fd.write(suffix)
                self.fd.flush()
                self.fd.seek(-len(suffix), 2)
            else:
                self.fd.flush()

    def newstate(self, state, prefix, suffix, html):
        if state != self.curstate:
            self.endstate()
            self.statesuffix = suffix
            self.curstate = state
            self.emit(prefix)
        self.emit(html, self.statesuffix)

    def timestamp(self, time):
        self.newstate('plain', '', '', '<span class="time">%s</span>' %
                      strftime('%Y-%m-%d %H:%M:%S', localtime(time)))

    def endstate(self):
        if self.curstate:
            self.emit(self.statesuffix)
            self.curstate = None

    def emit_toc(self, html):
        html = to_utf8(html)
        if self.fd_toc:
            self.fd_toc.write(html)
            self.fd_toc.flush()

    def toc_entry(self, level, text, target, cls=None):
        html = ''
        if self.toc_level < level:
            html += '<ul class="toc">' * (level - self.toc_level)
        elif self.toc_level > level:
            html += '</ul>' * (self.toc_level - level) + '\n'
        html += ('<li class="toc"><a href="content.html#%s" '
                 'target="content"%s>%s</a></li>\n' % (
                     target, cls and ' class="%s"' % cls or '',
                     escape(text)))
        self.emit_toc(html)
        self.toc_level = level

    def new_id(self):
        self.curid += 1
        return 'id%s-%s' % (id(self), self.curid)


class Handler(object):
    def __init__(self, log, plotformat):
        self.log = log
        self.plotformat = plotformat
        self.handlers = {}
        # register all handlers
        for name in Handler.__dict__:
            if name.startswith('handle_'):
                self.handlers[name[7:].replace('_', '/')] = getattr(self, name)

        self.dir = self.logdir = None
        self.out = HtmlWriter()

    def close(self):
        self.out.close()

    def handle_directory(self, time, data):
        directory, instr, proposal = data
        self.dir = directory
        self.logdir = path.join(directory, 'logbook')
        self.out.open(self.logdir, instr or 'NICOS', proposal)
        self.log.info('Opened new output files in ' + self.logdir)

    def handle_newexperiment(self, time, data):
        proposal, title = data
        targetid = self.out.new_id()
        if title:
            text = 'Experiment %s: %s' % (escape(proposal), escape(title))
        else:
            text = 'Experiment %s' % escape(proposal)
        self.out.timestamp(time)
        self.out.newstate('plain', '', '',
                          '<h1 id="%s">%s</h1>\n' % (targetid, text))
        self.out.toc_entry(1, text, targetid)

    def handle_setup(self, time, setupnames):
        self.out.timestamp(time)
        self.out.newstate('plain', '', '',
            '<p class="setup">New setup: %s</p>\n' %
            escape(', '.join(setupnames)))

    def handle_entry(self, time, data):
        self.out.timestamp(time)
        if creole:
            data, headers = creole.translate(data, self.out.new_id)
        else:
            data, headers = escape(data), []
        self.out.newstate('entry', '', '', data)
        for level, text, targetid in headers:
            self.out.toc_entry(level, text, targetid)

    def handle_remark(self, time, remark):
        targetid = self.out.new_id()
        self.out.timestamp(time)
        self.out.newstate('plain', '', '',
            '<h3 id="%s" class="remark">%s</h3>\n' % (targetid, escape(remark)))
        self.out.toc_entry(2, escape(remark), targetid)

    def handle_scriptbegin(self, time, data):
        self.out.timestamp(time)
        targetid = self.out.new_id()
        text = 'Script started: %s' % escape(data)
        #self.out.toc_entry(2, text, targetid)
        self.out.newstate('plain', '', '',
            '<p id="%s" class="scriptbegin">%s</p>\n' % (targetid, text))

    def handle_scriptend(self, time, data):
        self.out.timestamp(time)
        targetid = self.out.new_id()
        text = 'Script finished: %s' % escape(data)
        #self.out.toc_entry(2, text, targetid)
        self.out.newstate('plain', '', '',
            '<p id="%s" class="scriptend">%s</p>\n' % (targetid, text))

    def handle_sample(self, time, data):
        self.out.timestamp(time)
        text = 'New sample: %s' % escape(data)
        targetid = self.out.new_id()
        self.out.toc_entry(2, text, targetid, 'sample')
        self.out.newstate('plain', '', '',
            '<p id="%s" class="sample">%s</p>\n' % (targetid, text))

    def handle_detectors(self, time, dlist):
        self.out.timestamp(time)
        text = 'New standard detectors: %s' % escape(', '.join(dlist))
        targetid = self.out.new_id()
        self.out.toc_entry(2, text, targetid, 'detectors')
        self.out.newstate('plain', '', '',
            '<p id="%s" class="detectors">%s</p>\n' % (targetid, text))

    def handle_environment(self, time, dlist):
        self.out.timestamp(time)
        text = 'New standard environment: %s' % escape(', '.join(dlist))
        targetid = self.out.new_id()
        self.out.toc_entry(2, text, targetid, 'environment')
        self.out.newstate('plain', '', '',
            '<p id="%s" class="environment">%s</p>\n' % (targetid, text))

    def handle_offset(self, time, data):
        self.out.timestamp(time)
        dev, old, new = data
        self.out.newstate('plain', '', '',
            '<p class="offset"><b>Adjustment:</b> ' +
            escape('Offset of %s changed from %s to %s' % (dev, old, new))
            + '</p>\n')

    def handle_attachment(self, time, data):
        if not self.logdir:
            return
        description, fpaths, names = data
        links = []
        for fpath, name in zip(fpaths, names):
            fullname = path.join(self.logdir, name)
            oname = name
            i = 0
            while path.exists(fullname):
                i += 1
                name = oname + str(i)
                fullname = path.join(self.logdir, name)
            # using copyfile-unlink instead of shutil.move since we do not
            # want to keep a restrictive file mode set by the daemon
            copyfile(fpath, fullname)
            unlink(fpath)
            links.append('<a href="%s">%s</a>' % (name, escape(oname)))
        text = '<b>%s:</b> %s' % (escape(description) or 'Attachment',
                                  ' '.join(links))
        self.out.timestamp(time)
        self.out.newstate('plain', '', '', '<p class="attach">%s</p>\n' % text)

    def handle_message(self, time, message):
        formatted = formatMessage(message)
        if not formatted:
            return
        if message[2] == ERROR:
            self.out.newstate('messages_error',
                              '<div class="errblock"><pre class="messages">\n',
                              '</pre></div>\n', formatted)
        else:
            self.out.newstate('messages',
                '<div class="msgblock" onclick="hideshow(this)">'
                '<span class="msglabel">Messages</span>'
                '<pre class="messages">\n', '</pre></div>\n', formatted)

    #def handle_scanbegin(self, time, dataset):
    #    print 'Scan begin:', dataset

    def handle_scanend(self, time, dataset):
        names = '+'.join(dataset.xnames)
        headers = ['Scan#', 'Points']
        for xc in zip(dataset.xnames, dataset.xunits):
            headers.append('%s (%s)' % xc)
        ycindex = []
        for i, yc in enumerate(dataset.yvalueinfo):
            if yc.type == 'info' and 'file' in yc.name:
                ycindex.append(i)
                headers.append(yc.name)
        headers += ['Plot', 'Data']
        scannumber = dataset.sinkinfo.get('number', -1)
        if scannumber >= 0:
            html = ['<tr id="scan%s">' % scannumber]
            html.append('<td class="scannum">%s</td>' % scannumber)
        else:
            html = ['<tr>', '<td>-</td>']
        npoints = len(dataset.xresults)
        html.append('<td>%s</td>' % npoints)
        if dataset.xresults:
            for i in range(len(dataset.xnames)):
                if i < len(dataset.xnames) - dataset.envvalues:
                    first = dataset.xresults[0][i]
                    last = dataset.xresults[-1][i]
                else:
                    first = min((dataset.xresults[j][i] for j in range(npoints)),
                                key=lambda x: x or 0)
                    last = max((dataset.xresults[j][i] for j in range(npoints)),
                               key=lambda x: x or 0)
                fmtstr = dataset.xvalueinfo[i].fmtstr
                if first == last:
                    html.append('<td>%s</td>' % pretty1(fmtstr, first))
                else:
                    html.append('<td>%s</td>' % pretty2(fmtstr, first, last))
            for i in ycindex:
                first = path.splitext(path.basename(dataset.yresults[0][i]))[0]
                last = path.splitext(path.basename(dataset.yresults[-1][i]))[0]
                if first == last:
                    html.append('<td>%s</td>' % escape(first))
                else:
                    html.append('<td>%s - %s</td>' %
                                (escape(first), escape(last)))
        else:
            html.extend(['<td></td>'] * (len(dataset.xnames) + len(ycindex)))
        # plot link
        plotfmt = self.plotformat
        try:
            if self.logdir:
                plotDataset(dataset,
                            path.join(self.logdir, 'scan-%d' % scannumber),
                            plotfmt)
        except Exception:
            self.log.warning('could not generate plot', exc=1)
            html.append('<td>&mdash;</td>')
        else:
            html.append('<td><a href="scan-%d-lin.%s">Lin</a> / '
                        '<a href="scan-%d-log.%s">Log</a></td>' %
                        (scannumber, plotfmt, scannumber, plotfmt))
        # file link
        if self.logdir and dataset.sinkinfo.get('filepath'):
            relfile = path.relpath(dataset.sinkinfo.get('filepath'),
                                   self.logdir)
            html.append('<td><a href="%s" type="text/plain">File</a></td>'
                        % relfile)
        else:
            html.append('<td>...</td>')
        html.append('</tr>')
        headers = ''.join('<th width="%d%%">%s</th>' %
                          (100/len(headers), escape(h)) for h in headers)
        self.out.newstate('scan-' + names,
                          '<table class="scan"><tr class="head">' + headers
                          + '</tr>', '</table>\n', ''.join(html))
        if scannumber >= 0 and scannumber % 100 in (0, 50):
            self.out.toc_entry(3, 'Scan %d' % scannumber, 'scan%s' % scannumber)


# more ideas:
# - internal links -> reference scan numbers or attachments
# - integrated latex $foo$ syntax
