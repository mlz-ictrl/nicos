function init() {
    var handler = new Console();
    $(document).keydown(function(e) { handler.keydown(e); });
}

function Console() {
    this.window = $('#console');
    this.cursor = $('#cursor');
    this.input = $('#input')[0];
    res = $.ajax({url: '/json', dataType: 'json',
                  data: '{"method": "start_session", "params": [], "id": null}',
                  type: 'POST', async: false});
    this.sid = $.parseJSON(res.responseText).result;

    this._buffer = '';
    this._historyPosition = -1;
    this.history = [];

    this.prompt1 = $('<span class="prompt1">&gt;&gt;&gt; </span>');
    this.prompt2 = $('<span class="prompt2">... </span>');

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
    console.info('adding output ' + data.result);
    for (var i = 0; i < lines.length; i++)
        if (lines[i])
            $('<div>').text(lines[i]).
                addClass((data.error) ? 'traceback' : 'output').
                insertBefore(this.cursor);
    window.scrollBy(0, document.documentElement.scrollHeight);
}

Console.prototype.keydown = function(e) {
    var code = e.which;
    if (code == 13) {
        this.sendLine();
        this._stopKeyEvent(e);
        return false;
    } else if (code == 38 || code == 40) {
        /* 38 = up, 40 = down */
        if (code == 38 && this._historyPosition < this.history.length - 1)
            this._historyPosition++;
        if (code == 40 && this._historyPosition > -1)
            this._historyPosition--;
        if (this._historyPosition == -1)
            var line = '';
        else
            var line = this.history[this._historyPosition];
        this.input.value = line;
        this._stopKeyEvent(e);
        return false;
    }
}

Console.prototype.sendLine = function() {
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
        console.info('sending line ' + text);
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
    $('<span>').text(text).insertBefore(this.cursor);
}

Console.prototype._writePrompt = function() {
    if (this._buffer != '')
        this.prompt2.clone().insertBefore(this.cursor);
    else
        this.prompt1.clone().insertBefore(this.cursor);
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
