#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
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
# *****************************************************************************

"""Web interface for NICOS."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

CONSOLE_PAGE = r"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <script type="text/javascript">
/** keycodes for the events */
var KEYCODES = {
    8:  'backspace',   36: 'home',
    9:  'tab',         37: 'left',
    13: 'enter',       38: 'up',
    27: 'esc',         39: 'right',
    33: 'page up',     40: 'down',
    34: 'page down',   45: 'insert',
    35: 'end',         46: 'delete',
};
var AJAX_ACTIVEX = ['Msxml2.XMLHTTP', 'Microsoft.XMLHTTP', 'Msxml2.XMLHTTP.4.0'];
var CONSOLE_WIDTH = 115;

var webconsole = null;

/** initialize the application */
function init() {
    var handler = new Console();
    document.onkeydown = handler.keydown(handler);
}

/** log an error; currently it just alerts it */
function log(obj) {
    alert(json.toJSON(obj));
}

/** The AJAX Connection System */
var ajax = {
    UNINITIALIZED : 0,
    LOADING : 1,
    LOADED : 2,
    INTERACTIVE : 3,
    COMPLETE : 4,

    /** return a new ajax connection or null if not available */
    connect : function() {
        var con = null;
        try {
            con = new XMLHttpRequest();
        }
        catch (e) {
            if (typeof AJAX_ACTIVEX == 'string')
                con = new ActiveXObject(AJAX_ACTIVEX);
            else {
                for (var i=0; i < AJAX_ACTIVEX.length; i++) {
                    var axid = AJAX_ACTIVEX[i];
                    try {
                        con = new ActiveXObject(axid);
                    }
                    catch (e) {}
                    if (con) {
                        AJAX_ACTIVEX = axid;
                        break;
                    }
                }
            }
        }
        return con;
    },
    /** check if ajax is available */
    check : function() {
        return (this.connect() != null);
    },
    /** send a request to the server which calls the given callback method
        on each statechange */
    request : function(url, callback, method, post) {
        if (typeof post == 'undefined')
            post = null;
        if (typeof method == 'undefined')
            method = 'GET';
        var con = this.connect();
        con.onreadystatechange = function() {
            callback(con);
        };
        con.open(method, url);
        con.send(post);
    },
    /** send a request to the server and block the browser until the server
        has sent ajax.COMPLETE; return the connection object */
    call : function(url, method, post) {
        if (typeof post == 'undefined')
            post = null;
        if (typeof method == 'undefinied')
            method = 'GET';
        var con = this.connect();
        con.open(method, url, false);
        con.send(post);
        return con;
    },
}

var json = {
    /** eval a json string */
    fromJSON : function(s) {
        return eval('(' + s + ')');
    },
    /** create a json string out of a javascript structure */
    toJSON : function(o, keypos) {
        keypos = (typeof keypos != 'undefined') ? keypos : false;
        var objtype = typeof o;
        if (o == null) {
            if (keypos)
                return '"null"';
            return 'null';
        }
        if (objtype == 'number' || objtype == 'boolean') {
            if (keypos)
                return '"' + o + '"';
            return o + '';
        }
        if (objtype == 'string') {
            return '"' + o
                    .replace(/[\\]/g, '\\\\')
                    .replace(/["]/g,  '\\"')
                    .replace(/[\f]/g, '\\f')
                    .replace(/[\b]/g, '\\b')
                    .replace(/[\n]/g, '\\n')
                    .replace(/[\t]/g, '\\t')
                    .replace(/[\r]/g, '\\r')
                    + '"';
        }
        if (o instanceof Array) {
            var tmp = [];
            for (var i = 0; i < o.length; i++) {
                tmp.push(this.toJSON(o[i]));
            }
            return '[' + tmp.join(', ') + ']';
        }
        var tmp = [];
        for (var key in o) {
            var val = this.toJSON(o[key]);
            var key = this.toJSON(key, true);
            tmp.push(key + ': ' + val);
        }
        var result = '{' + tmp.join(', ') + '}';
        return result;
    },

    RPC : (function() {
        function rpc(url) {
            this.url = url;
        }
        rpc.prototype.createRequest = function(methodName, parameters) {
            return json.toJSON({
                method: methodName,
                params: parameters,
                id: null
            });
        }
        rpc.prototype.call = function(method) {
            var params = new Array();
            for (var i = 1; i < arguments.length; i++)
                params.push(arguments[i]);
            var request = this.createRequest(method, params);
            var con = ajax.call(this.url, 'POST', request);
            var response = json.fromJSON(con.responseText);
            if (response.error == null)
                return response.result;
            else
                log(response.error);
        }
        rpc.prototype.callback = function(callback, method) {
            var params = new Array();
            for (var i = 2; i < arguments.length; i++) {
                params.push(arguments[i]);
            }
            var request = this.createRequest(method, params);
            ajax.request(this.url, function(con) {
                if (con.readyState == ajax.COMPLETE) {
                    var response = json.fromJSON(con.responseText);
                    if (response.error == null)
                        callback(response.result);
                    else
                        log(response.error);
                }
            }, 'POST', request);
        }
        return rpc;
    })()
};

/** The Browser Console */
function Console() {
    webconsole = this;
    this.window = document.getElementById('console');
    this.cursor = document.getElementById('cursor');
    this.input = document.getElementById('input');
    this.connection = new json.RPC('/json');
    this.sid = this.connection.call('start_session');

    this._buffer = '';
    this._historyPosition = -1;
    this.history = [];

    this.prompt1 = document.createElement('SPAN');
    this.prompt1.appendChild(document.createTextNode('>>> '));
    this.prompt1.className = 'prompt1';

    this.prompt2 = document.createElement('SPAN');
    this.prompt2.appendChild(document.createTextNode('... '));
    this.prompt2.className = 'prompt2';
}

Console.prototype.keydown = function(self) {
    return function(e) {
        var e = (e) ? e : window.event;
        var code = (e.keyCode) ? e.keyCode : e.which;
        var mod = self._getMod(e);
        var key = null;
        key = KEYCODES[code];
        if (key == 'up' || key == 'down') {
            if (key == 'up' && self._historyPosition < self.history.length - 1)
                self._historyPosition++;
            if (key == 'down' && self._historyPosition > -1)
                self._historyPosition--;
            if (self._historyPosition == -1)
                var line = '';
            else
                var line = self.history[self._historyPosition];
            self.input.value = line;
            self._stopKeyEvent(e);
            return false;
        } else if (key == 'enter') {
            self.sendLine(key, mod);
            self._stopKeyEvent(e);
            return false;
        }
    }
}

/** send a line to the handler */
Console.prototype.sendLine = function(key, mod) {
    var text = this.input.value + '\n';
    var result;

    this._pushHistory(text);

    this._writePrompt();
    this._writeInput(text);

    text = this._buffer + text;

    // Check for multiline statements
    if (this._isMultiline(text)) {
        this._buffer = text;
        this.input.value = '';
    }
    else {
        // Send it!
        if (text != '\n') {
            result = this.connection.call('exec', this.sid, text);
            result.text = 'yay!';
            if (result.text) {
                var lines = [];
                var tlines = result.text.split('\n');
                for (var i = 0; i < tlines.length; i++) {
                    var src = tlines[i];
                    while (src) {
                        lines.push(src.substr(0, CONSOLE_WIDTH));
                        src = src.substr(CONSOLE_WIDTH);
                    }
                }
                for (var i = 0; i < lines.length; i++) {
                    var line = document.createElement('DIV');
                    line.className = (result.error) ? 'traceback' : 'output';
                    line.appendChild(document.createTextNode(lines[i]));
                    this.window.insertBefore(line, this.cursor);
                }
            }
        }
        this._historyPosition = -1;
        this._buffer = '';
        this.input.value = '';
    }
    document.body.scrollTop = document.body.scrollHeight;
}

Console.prototype._getMod = function(e) {
    var mod = [];
    if (e.ctrlKey)
        mod.push('ctrl');
    if (e.altKey || e.metaKey)
        mod.push('alt');
    if (e.shiftKey && e.charCode == 0)
        mod.push('shift');
    return mod;
}

Console.prototype._stopKeyEvent = function(e) {
    e.cancelBubble = true;
    if (e.stopPropagation)
        e.stopPropagation();
    if (e.preventDefault)
        e.preventDefault();
}

Console.prototype._writeInput = function(text) {
    var line = document.createElement('SPAN');
    line.appendChild(document.createTextNode(text));
    this.window.insertBefore(line, this.cursor);
}

Console.prototype._writePrompt = function() {
    if (this._buffer != '')
        this.window.insertBefore(this.prompt2.cloneNode(true), this.cursor);
    else
        this.window.insertBefore(this.prompt1.cloneNode(true), this.cursor);
}

Console.prototype._pushHistory = function(line) {
    if (line.charAt(line.length - 1) == '\n')
        line = line.substr(0, line.length - 1);
    if (this.history.length > 20)
        this.history.shift();
    this.history.unshift(line);
}

Console.prototype._isMultiline = function(text) {
    if (typeof this._inBlock == 'undefined')
        this._inBlock = false;

    function strCount(s, c) {
        var result = 0;
        var pos = -1;
        while (true) {
            var pos = s.indexOf(c, pos + 1);
            if (pos > -1) {
                result++;
            }
            else {
                return result;
            }
        }
    }
    // empty lines are always single line
    if (this._inBlock) {
        if (text.substr(text.length - 2) != '\n\n')
            return true;
        else
            this._inBlock = false;
    }
    if (text == '\n')
        return false;
    if (text.lastIndexOf(':') == text.length - 2 ||
        text.lastIndexOf('\\') == text.length - 2) {
        this._inBlock = true;
        return true;
    }
    if ((strCount(text, '(') > strCount(text, ')')) ||
        (strCount(text, '[') > strCount(text, ']')) ||
        (strCount(text, '{') > strCount(text, '}'))) {
        return true;
    }
    if (strCount(text, '""' + '"') % 2 != 0 ||
        strCount(text, "'''") % 2 != 0) {
        return true;
    }
    return false;
}
    </script>
    <style type="text/css">
        html {
            height: 100%;
        }
        body {
            height: 100%;
            margin: 0 auto;
            border-left: 1px solid #ccc;
            border-right: 1px solid #ccc;
            font-family: 'Luxi Sans', sans-serif;
            background: #eee;
        }
        #page {
            padding: 10px 20px;
        }
        #console {
            width: 100%;
            background: #fff;
            color: #111;
            border: 1px solid #888;
            font-family: 'Consolas', monospace;
        }
        #cursor {
            color: #111;
        }
        tt {
            font-family: 'Consolas', monospace;
        }
        #input {
            width: 100%;
            font-size: 100%;
            border: 1px solid #888;
            font-family: 'Consolas', monospace;
        }
        #execute {
            border: 1px solid #888;
            background-color: #eee;
            font-family: 'Consolas', monospace;
        }
        .prompt1 {
            color: olive;
        }
        .prompt2 {
            color: #888;
        }
        .output {
            color: navy;
        }
        .traceback {
            color: #cc0000;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div id="page">
        <pre id="console"><span style="color: #aaa">Welcome to the NICOS web console!
Enter commands in the input field below and press Enter.</span>
<span id="cursor">&nbsp;</span></pre>
        <input type="text" id="input" />
    </div>
    <script type="text/javascript">init();</script>
</body>
</html>
"""

import sys
import json
import logging
import traceback
from cgi import escape

from nicos import session
from nicos.loggers import NicosConsoleFormatter, DATEFMT

QUIT_MESSAGE = 'Just close the browser window to quit the session.'


class FakeInput(object):
    def read(self):
        return ''

    def readline(self):
        return '\n'

    def readlines(self):
        return []


class WebHandler(logging.Handler):
    """
    Log handler for transmitting log messages to the client.
    """

    def __init__(self, buffer):
        logging.Handler.__init__(self)
        self.setFormatter(NicosConsoleFormatter(datefmt=DATEFMT))
        self.buffer = buffer

    def emit(self, record):
        self.buffer.append(self.format(record) + '\n')


class NicosApp(object):
    """
    The nicos-web WSGI application.
    """

    def __init__(self):
        self._output_buffer = []

    def __call__(self, environ, start_response):
        status = '200 OK'
        try:
            path = environ['PATH_INFO'].strip('/')
            if not path:
                ctype = 'text/html'
                response = CONSOLE_PAGE
            else:
                ctype = 'text/javascript'
                response = self.json(environ)
        except Exception, err:
            ctype = 'text/plain'
            status = '500 Internal Server Error'
            response = 'Error: ' + escape(str(err))
        headers = [('Content-type', ctype)]
        start_response(status, headers)
        return [response]

    json_exports = {
        'start_session': '_start_session',
        'exec': '_exec'
    }

    def json(self, env):
        try:
            length = int(env['CONTENT_LENGTH'])
            request = json.loads(env['wsgi.input'].read(length))
        except:
            raise RuntimeError('bad request')
        try:
            if not request['method'] in self.json_exports:
                raise RuntimeError('method not found')
            handler = getattr(self, self.json_exports[request['method']])
            response = handler(*request['params'])
            return json.dumps({'id': request['id'], 'result': response,
                               'error': None})
        except Exception, e:
            try:
                errmsg, errtype = str(e), e.__class__.__name__
            except Exception:
                errmsg, errtype = 'unknown error', ''
            return json.dumps({'id': request['id'],
                               'result' : None,
                               'error': {'msg': errmsg, 'type': errtype}})

    def _start_session(self):
        return 'web'

    def _exec(self, sid, code):
        error = False
        try:
            try:
                code = compile(code, '<stdin>', 'single', 0, 1)
                exec code in session.getNamespace(), \
                             session.getLocalNamespace()
            except SystemExit:
                print QUIT_MESSAGE
            except:
                etype, value, tb = sys.exc_info()
                tb = tb.tb_next
                msg = ''.join(traceback.format_exception(etype, value, tb))
                session.log.error(msg.rstrip())
                error = True
        finally:
            output = ''.join(self._output_buffer)
            del self._output_buffer[:]
        return {'error': error, 'text': output}
