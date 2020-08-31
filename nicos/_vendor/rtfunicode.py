# pylint: skip-file

# Encode unicode strings to RTF 1.5-compatible command codes.
# Command codes are of the form `\uN?`, where N is a signed 16-bit integer and
# ? is a placeholder character for pre-1.5 RTF readers.

from __future__ import absolute_import, division, print_function

import codecs
import re

# Encode everything < 0x20, the \, { and } characters and everything > 0x7f
_charescape = '([\x00-\x1f\\\\{}\x80-\uffff])'

_charescape = re.compile(_charescape)


# This triggers a pyflakes warnings (redefinition), please ignore.
# Use a `.format()` string formatter.
def _replace(match):
    cp = ord(match.group(1))
    # Convert codepoint into a signed integer, insert into escape sequence
    return '\\u{0}?'.format(cp > 32767 and cp - 65536 or cp)


def _rtfunicode_encode(text, errors):
    # Encode to RTF \uDDDDD? signed 16 integers and replacement char
    return _charescape.sub(_replace, text).encode('ascii', errors)



class Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        return _rtfunicode_encode(input, errors), len(input)


class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=False):
        return _rtfunicode_encode(input, self.errors)


class StreamWriter(Codec, codecs.StreamWriter):
    pass


def rtfunicode(name):
    if name == 'rtfunicode':
        return codecs.CodecInfo(
            name='rtfunicode',
            encode=Codec().encode,
            decode=Codec().decode,  # raises NotImplementedError
            incrementalencoder=IncrementalEncoder,
            streamwriter=StreamWriter,
        )


codecs.register(rtfunicode)
