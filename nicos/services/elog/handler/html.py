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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""The NICOS electronic logbook."""

from html import escape
from logging import ERROR
from os import path
from shutil import copyfile
from time import localtime, strftime

from nicos.core import Param, oneof
from nicos.services.elog.genplot import plotDataset
from nicos.services.elog.handler import Handler as BaseHandler
from nicos.services.elog.utils import create_or_open, formatMessage, pretty1, \
    pretty2

try:
    import markdown
except ImportError:
    markdown = None
else:
    class CollectHeaders(markdown.Extension):
        """Markdown extension that assigns proper IDs to headers, and maintains
        a list of headers that can be added to the elog's table of contents.
        """
        def __init__(self, new_id_func):
            markdown.Extension.__init__(self)
            self.new_id = new_id_func
            self.headers = []

        def extendMarkdown(self, md):
            md.registerExtension(self)
            md.treeprocessors.register(CollectHeadersProcessor(self),
                                       'collect-headers', 999)

    class CollectHeadersProcessor(markdown.treeprocessors.Treeprocessor):
        def __init__(self, ext):
            markdown.treeprocessors.Treeprocessor.__init__(self)
            self.ext = ext

        def run(self, root):
            for level in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
                for head in root.iter(level):
                    head.attrib['id'] = self.ext.new_id()
                    self.ext.headers.append((
                        int(level[1:]),
                        head.text,
                        head.attrib['id'],
                    ))


FRAMESET = """\
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>%s logbook: %s</title>
</head>
<frameset cols="25%%,*">
<frame src="toc.html">
<frame src="content.html" name="content">
</frameset>
</html>
"""

PROLOG = b"""\
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
"""

PROLOG_TOC = b"""\
<p class="showlinks">
  <a href="javascript:parent.content.msgshow()">Show all messages</a><br>
  <a href="javascript:parent.content.msghide()">Hide all messages</a>
</p>
<p class="contenthead">Contents</p>
"""


class HtmlWriter:
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
            self.fd = None
        if self.fd_toc:
            self.fd_toc.write(b'</ul>' * self.toc_level)
            self.fd_toc.close()
            self.fd_toc = None
        self.toc_level = 0

    def open(self, directory, instr, proposal):
        self.close()
        with open(path.join(directory, 'logbook.html'), 'w',
                  encoding='utf-8') as f:
            f.write(FRAMESET % (instr, proposal))
        self.fd = create_or_open(path.join(directory, 'content.html'), PROLOG)
        self.fd_toc = create_or_open(path.join(directory, 'toc.html'),
                                     PROLOG_TOC)

    def emit(self, html, suffix=''):
        html = html.encode()
        suffix = suffix.encode()
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
        html = html.encode()
        if self.fd_toc:
            self.fd_toc.write(html)
            self.fd_toc.flush()

    def toc_entry(self, level, text, target, cls=None):
        htmlstr = ''
        if self.toc_level < level:
            htmlstr += '<ul class="toc">' * (level - self.toc_level)
        elif self.toc_level > level:
            htmlstr += '</ul>' * (self.toc_level - level) + '\n'
        htmlstr += ('<li class="toc"><a href="content.html#%s" '
                    'target="content"%s>%s</a></li>\n' % (
                        target, cls and ' class="%s"' % cls or '',
                        escape(text)))
        self.emit_toc(htmlstr)
        self.toc_level = level

    def new_id(self):
        self.curid += 1
        return 'id%s-%s' % (id(self), self.curid)


class Handler(BaseHandler):
    parameters = {
        'plotformat': Param('Format for scan plots', type=oneof('svg', 'png')),
    }

    def doInit(self, mode):
        BaseHandler.doInit(self, mode)
        self._out = HtmlWriter()

    def doShutdown(self):
        self._out.close()

    def handle_directory(self, time, data):
        BaseHandler.handle_directory(self, time, data)
        self._out.open(self._logdir, self._instr or 'NICOS', self._proposal)
        self.log.info('Opened new output files in %s', self._logdir)

    def handle_newexperiment(self, time, data):
        BaseHandler.handle_newexperiment(self, time, data)
        targetid = self._out.new_id()
        if self._title:
            text = 'Experiment %s: %s' % (escape(self._proposal), escape(self._title))
        else:
            text = 'Experiment %s' % escape(self._proposal)
        self._out.timestamp(time)
        self._out.newstate('plain', '', '',
                           '<h1 id="%s">%s</h1>\n' % (targetid, text))
        self._out.toc_entry(1, text, targetid)

    def handle_setup(self, time, setupnames):
        self._out.timestamp(time)
        self._out.newstate('plain', '', '',
                           '<p class="setup">New setup: %s</p>\n' %
                           escape(', '.join(setupnames)))

    def handle_entry(self, time, data):
        self._out.timestamp(time)
        if markdown:
            header_ext = CollectHeaders(self._out.new_id)
            data = markdown.markdown(data, extensions=[
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                header_ext,
            ])
            headers = header_ext.headers
        else:
            data, headers = escape(data), []
        self._out.newstate('entry', '', '', data)
        for level, text, targetid in headers:
            self._out.toc_entry(level, text, targetid)

    def handle_remark(self, time, remark):
        targetid = self._out.new_id()
        self._out.timestamp(time)
        self._out.newstate('plain', '', '',
                           '<h3 id="%s" class="remark">%s</h3>\n' %
                           (targetid, escape(remark)))
        self._out.toc_entry(2, escape(remark), targetid)

    def handle_scriptbegin(self, time, script):
        self._out.timestamp(time)
        targetid = self._out.new_id()
        text = 'Script started: %s' % escape(script)
        # self._out.toc_entry(2, text, targetid)
        self._out.newstate('plain', '', '',
                           '<p id="%s" class="scriptbegin">%s</p>\n' %
                           (targetid, text))

    def handle_scriptend(self, time, script):
        self._out.timestamp(time)
        targetid = self._out.new_id()
        text = 'Script finished: %s' % escape(script)
        # self._out.toc_entry(2, text, targetid)
        self._out.newstate('plain', '', '',
                           '<p id="%s" class="scriptend">%s</p>\n' %
                           (targetid, text))

    def handle_sample(self, time, sample):
        self._out.timestamp(time)
        text = 'New sample: %s' % escape(sample)
        targetid = self._out.new_id()
        self._out.toc_entry(2, text, targetid, 'sample')
        self._out.newstate('plain', '', '',
                           '<p id="%s" class="sample">%s</p>\n' %
                           (targetid, text))

    def handle_detectors(self, time, dlist):
        self._out.timestamp(time)
        text = 'New standard detectors: %s' % escape(', '.join(dlist))
        targetid = self._out.new_id()
        self._out.toc_entry(2, text, targetid, 'detectors')
        self._out.newstate('plain', '', '',
                           '<p id="%s" class="detectors">%s</p>\n' %
                           (targetid, text))

    def handle_environment(self, time, elist):
        self._out.timestamp(time)
        text = 'New standard environment: %s' % escape(', '.join(elist))
        targetid = self._out.new_id()
        self._out.toc_entry(2, text, targetid, 'environment')
        self._out.newstate('plain', '', '',
                           '<p id="%s" class="environment">%s</p>\n' %
                           (targetid, text))

    def handle_offset(self, time, data):
        self._out.timestamp(time)
        dev, old, new = data
        self._out.newstate('plain', '', '',
                           '<p class="offset"><b>Adjustment:</b> ' +
                           escape('Offset of %s changed from %s to %s' %
                                  (dev, old, new))
                           + '</p>\n')

    def handle_attachment(self, time, data):
        if not self._logdir:
            return
        description, fpaths, names = data
        links = []
        for fpath, name in zip(fpaths, names):
            fullname = path.join(self._logdir, name)
            oname = name
            i = 0
            while path.exists(fullname):
                i += 1
                name = oname + str(i)
                fullname = path.join(self._logdir, name)
            # using copyfile instead of shutil.move since we do not
            # want to keep a restrictive file mode set by the daemon
            copyfile(fpath, fullname)
            links.append('<a href="%s">%s</a>' % (name, escape(oname)))
        text = '<b>%s:</b> %s' % (escape(description) or 'Attachment',
                                  ' '.join(links))
        self._out.timestamp(time)
        self._out.newstate('plain', '', '', '<p class="attach">%s</p>\n' % text)

    def handle_image(self, time, data):
        description, fpaths, extensions, names = data
        svgs = [(p, n) for (p, n, e) in zip(fpaths, names, extensions) if
                e.lower() == '.svg']
        if svgs:  # prefer .svg format
            fpaths, names = zip(*svgs)
        self.handle_attachment(time, [description, fpaths, names])

    def handle_message(self, time, message):
        formatted = formatMessage(message)
        if not formatted:
            return
        if message[2] == ERROR:
            self._out.newstate('messages_error',
                               '<div class="errblock"><pre class="messages">\n',
                               '</pre></div>\n', formatted)
        else:
            self._out.newstate('messages',
                               '<div class="msgblock" onclick="hideshow(this)">'
                               '<span class="msglabel">Messages</span>'
                               '<pre class="messages">\n', '</pre></div>\n',
                               formatted)

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
        scannumber = dataset.counter or -1
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
            if self._logdir:
                plotDataset(dataset,
                            path.join(self._logdir, 'scan-%d' % scannumber),
                            plotfmt)
        except Exception:
            self.log.warning('could not generate plot', exc=1)
            html.append('<td>&mdash;</td>')
        else:
            html.append('<td><a href="scan-%d-lin.%s">Lin</a> / '
                        '<a href="scan-%d-log.%s">Log</a></td>' %
                        (scannumber, plotfmt, scannumber, plotfmt))
        # file link
        if self._logdir and dataset.filepaths:
            relfile = path.relpath(dataset.filepaths[0], self._logdir)
            html.append('<td><a href="%s" type="text/plain">File</a></td>'
                        % relfile)
        else:
            html.append('<td>...</td>')
        html.append('</tr>')
        headers = ''.join('<th width="%d%%">%s</th>' %
                          (100//len(headers), escape(h)) for h in headers)
        self._out.newstate('scan-' + names,
                           '<table class="scan"><tr class="head">' + headers
                           + '</tr>', '</table>\n', ''.join(html))
        if scannumber >= 0 and scannumber % 50 == 0:
            self._out.toc_entry(3, 'Scan %d' % scannumber, 'scan%s' % scannumber)


# more ideas:
# - integrated latex $foo$ syntax
