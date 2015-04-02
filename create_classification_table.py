#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

# Copyright (c) 2015 Code for Karlsruhe (http://codefor.de/karlsruhe)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Generate character classification table for image OCR.

The homepage from which we scrape our data uses the GD graphics
library to generate its diagrams. This script uses the same library
to produce a sample image containing all characters from which a
classification map is constructed. The map is printed to STDOUT.
"""

import gd


def create_text_image(text, f, font=gd.gdFontLarge):
    """
    Create image with text.

    ``text`` is the text which should be printed to the image and ``f``
    is an open file-like object.

    The resulting image is written to ``f`` in PNG format.
    """
    text_width, text_height = gd.fontstrsize(font, text)
    img = gd.image((text_width + 2, text_height + 2))
    black = img.colorAllocate((0, 0, 0))
    white = img.colorAllocate((255, 255, 255))
    img.fill((0, 0), white)
    img.string(font, (1, 1), text, black)
    img.writePng(f)


if __name__ == '__main__':
    import collections
    import os
    import pprint
    import sys
    import tempfile

    import PIL.Image

    from scrape import get_char_signatures

    # We don't use ASCII char 34 (double quotes) because it is not
    # connected and our OCR cannot handle such chars. We don't use
    # char 39 (single quote) because in that font it is a translated
    # version of "," and our OCR cannot distinguish them.
    chars = ''.join(chr(i) for i in range(33, 127) if i not in [34, 39])

    f = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    try:
        create_text_image(chars, f)
        f.seek(0)
        img = PIL.Image.open(f).convert('L')
    finally:
        try:
            f.close()
        except:
            pass
        try:
            os.unlink(f.name)
        except:
            pass

    sigs = get_char_signatures(img, space_width=float('Inf'))

    if len(chars) != len(sigs):
        sys.exit('Got %d chars in string but %d chars in image.' % (len(chars), len(sigs)))

    table = collections.OrderedDict()
    table[tuple()] = ' '
    for char, sig in zip(chars, sigs):
        if sig in table:
            print "Warning: Duplicate sig %s for chars '%s' and '%s'." % (sig, table[sig], char)
        else:
            table[sig] = char

    print '{'
    for item in table.iteritems():
        print '    %r: %r,' % item
    print '}'

