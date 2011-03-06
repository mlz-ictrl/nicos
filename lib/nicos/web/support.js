var KEYCODES = {
    8:  'backspace',   36: 'home',
    9:  'tab',         37: 'left',
    13: 'enter',       38: 'up',
    27: 'esc',         39: 'right',
    33: 'page up',     40: 'down',
    34: 'page down',   45: 'insert',
    35: 'end',         46: 'delete',
};

var webconsole = null;

function init() {
    var handler = new Console();
    document.onkeydown = handler.keydown(handler);
}

function Console() {
    webconsole = this;
    this.window = document.getElementById('console');
    this.cursor = document.getElementById('cursor');
    this.input = document.getElementById('input');
    res = $.ajax({url: '/json', dataType: 'json',
                  data: '{"method": "start_session", "params": [], "id": null}',
                  type: 'POST', async: false});
    this.sid = $.parseJSON(res.responseText).result;

    this._buffer = '';
    this._historyPosition = -1;
    this.history = [];

    this.prompt1 = document.createElement('SPAN');
    this.prompt1.appendChild(document.createTextNode('>>> '));
    this.prompt1.className = 'prompt1';

    this.prompt2 = document.createElement('SPAN');
    this.prompt2.appendChild(document.createTextNode('... '));
    this.prompt2.className = 'prompt2';

    this.getOutput();
}

Console.prototype.stringToJSON = function(o) {
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

Console.prototype.getOutput = function() {
    var self = this;
    $.ajax({url: '/json', dataType: 'json',
            data: '{"method": "output", "params": ["' + this.sid + '"], "id": null}',
            type: 'POST', success: function(data) {
                if (data.result)
                    self.addOutput(data);
                self.getOutput();
            }
           });
}

Console.prototype.addOutput = function(data) {
    var lines = data.result.split('\n');
    for (var i = 0; i < lines.length; i++) {
        var line = document.createElement('DIV');
        line.className = (data.error) ? 'traceback' : 'output';
        line.appendChild(document.createTextNode(lines[i]));
        this.window.insertBefore(line, this.cursor);
    }
    window.scrollBy(0, document.documentElement.scrollHeight);
}

Console.prototype.keydown = function(self) {
    return function(e) {
        var e = (e) ? e : window.event;
        var code = (e.keyCode) ? e.keyCode : e.which;
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
            self.sendLine(key);
            self._stopKeyEvent(e);
            return false;
        }
    }
}

Console.prototype.sendLine = function(key) {
    var text = this.input.value + '\n';
    var result;

    this._pushHistory(text);

    this._writePrompt();
    this._writeInput(text);

    text = this._buffer + text;

    if (this._isMultiline(text)) {
        this._buffer = text;
        this.input.value = '';
    }
    else if (text != '\n') {
        $.ajax({url: '/json', dataType: 'json',
            data: '{"method": "exec", "params": ["' + this.sid + '", '
                + this.stringToJSON(text) + '], "id": null}',
            type: 'POST', success: function(data) {
            }
           });
        this._historyPosition = -1;
        this._buffer = '';
        this.input.value = '';
    }
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
