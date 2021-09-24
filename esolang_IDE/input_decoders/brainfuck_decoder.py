import re
import codecs

from .base_decoder import BaseDecoder


class BrainfuckDecoder(BaseDecoder):
    REGEX = re.compile(r'\\(?:n|r|t|\\|\d{1,3})|[^\\]', flags=re.DOTALL)

    @classmethod
    def decode_next(cls, text):
        match_obj = re.match(cls.REGEX, text)
        if match_obj is None:
            return None, 0

        # Matched string
        match = match_obj[0]

        # A match of length 1 means that the match was just a standard chararacter.
        # A match of more than length 1 means that the match was an escape sequence
        if len(match) > 1:
            if match[1].isdecimal():
                # Ascii code
                match = chr(int(match[1:]))
            else:
                # Escape character (\n, \r, \t)
                match = codecs.decode(match, 'unicode_escape')
        return match, match_obj.end()