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
Scraper for Karlsruhe's drinking water quality indicators.

This script scrapes the values of several drinking water quality
indicators from the homepage of the Stadtwerke Karlsruhe.
"""

import cStringIO
import contextlib
import datetime
import locale
import urllib2

import PIL.Image


# Homepage:
# http://www.stadtwerke-karlsruhe.de/swka-de/inhalte/produkte/trinkwasser/online-wert-trinkwasser.php

IMAGE_URL = "http://www.stadtwerke-karlsruhe.de/cgi-bin/gd?h=%d&w=%d&r=255&g=255&b=255&tr=0&tg=0&tb=0&wert=%s&tt=%%20%%20%%20&wnull=0&wmax=25"


VALUES = {
    'w1': ('temperature', '°C'),
    'w2': ('ph', ''),
    'w3': ('conductivity', 'µS/cm'),
    'w4': ('turbidity', 'NTU'),
    'w5': ('oxygen', 'mg/l'),
    'w6': ('nitrate', 'mg/l'),
}

def get_image(key, width, height):
    """
    Download one of the images/diagrams.

    ``key`` is the diagram key (``w1`` to ``w6`` for the indicators,
    ``w9`` for the date image). ``width`` and ``height`` specify the
    image dimensions.

    The return value is a ``PIL.Image.Image`` instance from which the
    black border has been cropped.
    """
    buf = cStringIO.StringIO(urllib2.urlopen(IMAGE_URL % (height, width, key)).read())
    img = PIL.Image.open(buf)
    return img.crop((1, 1, img.size[0] - 2, img.size[1] - 2))  # Cut 1 pixel border


def count_black_pixels(img, left=None, top=None, right=None, bottom=None):
    """
    Count black pixels in an image row- and column-wise.

    The black pixels in ``img`` are counted row- and column-wise and
    the result is returned as a 2-tuple.

    ``left``, ``top``, ``right`` and ``bottom`` specify the borders of
    the counting area. If not specified they default to the respective
    image border (e.g. ``top`` defaults to 0). ``left`` and ``top`` are
    inclusive, ``right`` and ``bottom`` are exclusive.
    """
    columns = img.size[0]
    if left is None:
        left = 0
    if top is None:
        top = 0
    if right is None:
        right = columns
    if bottom is None:
        bottom = img.size[1]
    data = img.getdata()
    hcount = [0] * (bottom - top)
    vcount = [0] * (right - left)
    for x in range(left, right):
        for y in range(top, bottom):
            if not data[x + y * columns]:
                hcount[y - top] += 1
                vcount[x - left] += 1
    return hcount, vcount


def get_block_signature(img, left, top, right, bottom):
    """
    Get an image block's signature.

    The signature is a list of the running indices of the black pixels
    in the block.

    ``left``, ``top``, ``right`` and ``bottom`` specify the borders of
    the block. ``left`` and ``top`` are inclusive, ``right`` and
    ``bottom`` are exclusive.
    """
    columns = img.size[0]
    data = img.getdata()
    sig = []
    width = right - left
    for y in range(top, bottom):
        for x in range(left, right):
            index = x + y * columns
            if not data[index]:
                sig.append((x - left) + width * (y - top))
    return tuple(sig)


def split(seq):
    """
    Split a sequence on zeros.

    The given sequence is split into chunks separated by one or more
    zeros. The start (inclusive) and end (exclusive) indices of the
    chunks are returned as a list of 2-tuples.
    """
    indices = []
    start = None
    for i, s in enumerate(seq):
        if start is None and s:
            start = i
        elif start is not None and not s:
            indices.append((start, i))
            start = None
    if start is not None:
        indices.append((start, len(seq)))
    return indices


def strip(seq):
    """
    Strip zeros from the front and end of a sequence.

    Returns a tuple of the first and last non-zero items' indices.
    """
    indices = split(seq)
    return indices[0][0], indices[-1][1]


def get_char_signatures(img, space_width=6):
    """
    Get character signatures for an image.

    The image is assumed to contain one row of characters, each of
    which is connected. The return value is a list of character
    signatures for these characters.

    If the gap between two characters is equal to or larger than
    ``space_width`` then a space signature (an empty tuple) is
    inserted between the characters' signatures.
    """
    signatures = []
    img = img.convert('L')
    vcount = count_black_pixels(img)[1]
    chars = []
    last_right = float('Inf')
    for left, right in split(vcount):
        if left - last_right >= space_width:
            signatures.append(())  # Space
        hcount = count_black_pixels(img, left=left, right=right)[0]
        top, bottom = strip(hcount)
        signatures.append(get_block_signature(img, left, top, right, bottom))
        last_right = right
    return signatures


# This table was generated using ``create_classification_table.py``.
CLASSES = {
    (): ' ',
    (0, 1, 2, 3, 4, 5, 6, 8, 9): '!',
    (2, 5, 8, 11, 14, 17, 18, 19, 20, 21, 22, 23, 25, 28, 31, 34, 36, 37, 38, 39, 40, 41, 42, 45, 48, 51, 54, 57): '#',
    (3, 8, 9, 10, 11, 12, 14, 17, 20, 21, 24, 29, 30, 31, 38, 39, 40, 45, 48, 49, 52, 55, 57, 58, 59, 60, 61, 66): '$',
    (1, 2, 6, 7, 10, 12, 14, 17, 19, 22, 23, 25, 31, 38, 44, 46, 47, 50, 52, 55, 57, 59, 62, 63, 67, 68): '%',
    (2, 3, 4, 8, 12, 15, 19, 22, 26, 30, 31, 32, 36, 37, 38, 41, 42, 46, 48, 49, 54, 56, 60, 61, 64, 65, 66, 69): '&',
    (2, 4, 7, 9, 12, 15, 18, 21, 24, 28, 31, 35): '(',
    (0, 4, 7, 11, 14, 17, 20, 23, 26, 28, 31, 33): ')',
    (3, 7, 10, 13, 15, 17, 19, 23, 24, 25, 29, 31, 33, 35, 38, 41, 45): '*',
    (3, 10, 17, 21, 22, 23, 24, 25, 26, 27, 31, 38, 45): '+',
    (0, 1, 3, 5, 6): ',',
    (0, 1, 2, 3, 4, 5): '-',
    (0, 1, 2, 3): '.',
    (5, 11, 16, 21, 27, 32, 38, 43, 48, 54): '/',
    (2, 3, 7, 10, 12, 17, 18, 23, 24, 29, 30, 35, 36, 41, 42, 47, 49, 52, 56, 57): '0',
    (2, 6, 7, 10, 12, 17, 22, 27, 32, 37, 42, 45, 46, 47, 48, 49): '1',
    (1, 2, 3, 4, 6, 11, 12, 17, 23, 27, 28, 32, 37, 42, 48, 54, 55, 56, 57, 58, 59): '2',
    (1, 2, 3, 4, 6, 11, 12, 17, 23, 26, 27, 28, 35, 41, 42, 47, 48, 53, 55, 56, 57, 58): '3',
    (4, 9, 10, 14, 16, 19, 22, 24, 28, 30, 34, 36, 37, 38, 39, 40, 41, 46, 52, 58): '4',
    (0, 1, 2, 3, 4, 5, 6, 12, 18, 24, 25, 26, 27, 28, 35, 41, 47, 48, 53, 55, 56, 57, 58): '5',
    (2, 3, 4, 7, 12, 18, 24, 25, 26, 27, 28, 30, 35, 36, 41, 42, 47, 48, 53, 55, 56, 57, 58): '6',
    (0, 1, 2, 3, 4, 5, 11, 17, 22, 28, 34, 39, 45, 51, 57): '7',
    (1, 2, 3, 4, 6, 11, 12, 17, 18, 23, 25, 26, 27, 28, 30, 35, 36, 41, 42, 47, 48, 53, 55, 56, 57, 58): '8',
    (1, 2, 3, 4, 6, 11, 12, 17, 18, 23, 25, 26, 27, 28, 29, 35, 41, 47, 52, 55, 56, 57): '9',
    (0, 1, 2, 3, 10, 11, 12, 13): ':',
    (0, 1, 2, 3, 10, 11, 13, 15, 16): ';',
    (4, 8, 12, 16, 20, 26, 32, 38, 44): '<',
    (0, 1, 2, 3, 4, 5, 24, 25, 26, 27, 28, 29): '=',
    (0, 6, 12, 18, 24, 28, 32, 36, 40): '>',
    (1, 2, 3, 4, 6, 11, 12, 17, 23, 28, 33, 39, 51, 57): '?',
    (2, 3, 4, 7, 11, 12, 15, 17, 18, 20, 22, 23, 24, 26, 29, 30, 32, 35, 36, 38, 41, 42, 45, 46, 47, 49, 56, 57, 58, 59): '@',
    (2, 3, 7, 10, 12, 17, 18, 23, 24, 29, 30, 31, 32, 33, 34, 35, 36, 41, 42, 47, 48, 53, 54, 59): 'A',
    (0, 1, 2, 3, 4, 6, 11, 12, 17, 18, 23, 24, 25, 26, 27, 28, 30, 35, 36, 41, 42, 47, 48, 53, 54, 55, 56, 57, 58): 'B',
    (1, 2, 3, 4, 6, 11, 12, 18, 24, 30, 36, 42, 48, 53, 55, 56, 57, 58): 'C',
    (0, 1, 2, 3, 6, 10, 12, 17, 18, 23, 24, 29, 30, 35, 36, 41, 42, 47, 48, 52, 54, 55, 56, 57): 'D',
    (0, 1, 2, 3, 4, 5, 6, 12, 18, 24, 25, 26, 27, 28, 30, 36, 42, 48, 54, 55, 56, 57, 58, 59): 'E',
    (0, 1, 2, 3, 4, 5, 6, 12, 18, 24, 25, 26, 27, 28, 30, 36, 42, 48, 54): 'F',
    (1, 2, 3, 4, 6, 11, 12, 18, 24, 30, 33, 34, 35, 36, 41, 42, 47, 48, 52, 53, 55, 56, 57, 59): 'G',
    (0, 5, 6, 11, 12, 17, 18, 23, 24, 25, 26, 27, 28, 29, 30, 35, 36, 41, 42, 47, 48, 53, 54, 59): 'H',
    (0, 1, 2, 3, 4, 7, 12, 17, 22, 27, 32, 37, 42, 45, 46, 47, 48, 49): 'I',
    (3, 4, 5, 10, 16, 22, 28, 34, 40, 42, 46, 48, 52, 55, 56, 57): 'J',
    (0, 5, 6, 10, 12, 15, 18, 20, 24, 25, 30, 31, 36, 38, 42, 45, 48, 52, 54, 59): 'K',
    (0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 55, 56, 57, 58, 59): 'L',
    (0, 6, 7, 8, 12, 13, 14, 15, 19, 20, 21, 23, 25, 27, 28, 30, 32, 34, 35, 38, 41, 42, 45, 48, 49, 55, 56, 62, 63, 69): 'M',
    (0, 5, 6, 7, 11, 12, 13, 17, 18, 20, 23, 24, 26, 29, 30, 33, 35, 36, 39, 41, 42, 46, 47, 48, 52, 53, 54, 59): 'N',
    (1, 2, 3, 4, 6, 11, 12, 17, 18, 23, 24, 29, 30, 35, 36, 41, 42, 47, 48, 53, 55, 56, 57, 58): 'O',
    (0, 1, 2, 3, 4, 6, 11, 12, 17, 18, 23, 24, 25, 26, 27, 28, 30, 36, 42, 48, 54): 'P',
    (1, 2, 3, 4, 7, 12, 14, 19, 21, 26, 28, 33, 35, 40, 42, 47, 49, 51, 52, 54, 56, 57, 60, 61, 64, 65, 66, 67, 75, 76): 'Q',
    (0, 1, 2, 3, 4, 6, 11, 12, 17, 18, 23, 24, 25, 26, 27, 28, 30, 33, 36, 40, 42, 46, 48, 53, 54, 59): 'R',
    (1, 2, 3, 4, 6, 11, 12, 17, 18, 25, 26, 33, 34, 41, 42, 47, 48, 53, 55, 56, 57, 58): 'S',
    (0, 1, 2, 3, 4, 5, 6, 10, 17, 24, 31, 38, 45, 52, 59, 66): 'T',
    (0, 5, 6, 11, 12, 17, 18, 23, 24, 29, 30, 35, 36, 41, 42, 47, 48, 53, 55, 56, 57, 58): 'U',
    (0, 6, 7, 13, 14, 20, 22, 26, 29, 33, 36, 40, 44, 46, 51, 53, 59, 66): 'V',
    (0, 6, 7, 13, 14, 20, 21, 24, 27, 28, 31, 34, 35, 38, 41, 42, 45, 48, 49, 51, 53, 55, 56, 58, 60, 62, 64, 68): 'W',
    (0, 5, 6, 11, 13, 16, 19, 22, 26, 27, 32, 33, 37, 40, 43, 46, 48, 53, 54, 59): 'X',
    (0, 6, 7, 13, 15, 19, 22, 26, 30, 32, 38, 45, 52, 59, 66): 'Y',
    (0, 1, 2, 3, 4, 5, 11, 17, 22, 27, 32, 37, 42, 48, 54, 55, 56, 57, 58, 59): 'Z',
    (0, 1, 2, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 34, 35): '[',
    (0, 6, 13, 20, 26, 33, 39, 46, 53, 59): '\\',
    (0, 1, 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 33, 34, 35): ']',
    (2, 3, 7, 10, 12, 17): '^',
    (0, 1, 2, 3, 4, 5, 6): '_',
    (0, 1, 2, 4, 7): '`',
    (1, 2, 3, 4, 6, 11, 15, 16, 17, 19, 20, 23, 24, 29, 30, 34, 35, 37, 38, 39, 41): 'a',
    (0, 6, 12, 18, 20, 21, 22, 24, 25, 29, 30, 35, 36, 41, 42, 47, 48, 49, 53, 54, 56, 57, 58): 'b',
    (1, 2, 3, 4, 6, 11, 12, 18, 24, 30, 35, 37, 38, 39, 40): 'c',
    (5, 11, 17, 19, 20, 21, 23, 24, 28, 29, 30, 35, 36, 41, 42, 47, 48, 52, 53, 55, 56, 57, 59): 'd',
    (1, 2, 3, 4, 6, 11, 12, 17, 18, 19, 20, 21, 22, 23, 24, 30, 37, 38, 39, 40): 'e',
    (2, 3, 4, 7, 11, 13, 19, 24, 25, 26, 27, 28, 31, 37, 43, 49, 55): 'f',
    (5, 7, 8, 9, 11, 12, 16, 18, 22, 24, 28, 31, 32, 33, 37, 43, 44, 45, 46, 48, 53, 54, 59, 61, 62, 63, 64): 'g',
    (0, 6, 12, 18, 20, 21, 22, 24, 25, 29, 30, 35, 36, 41, 42, 47, 48, 53, 54, 59): 'h',
    (2, 7, 16, 17, 22, 27, 32, 37, 42, 45, 46, 47, 48, 49): 'i',
    (4, 9, 18, 19, 24, 29, 34, 39, 44, 49, 54, 55, 58, 61, 62): 'j',
    (0, 6, 12, 18, 22, 24, 27, 30, 32, 36, 37, 38, 42, 45, 48, 52, 54, 59): 'k',
    (1, 2, 7, 12, 17, 22, 27, 32, 37, 42, 45, 46, 47, 48, 49): 'l',
    (0, 1, 2, 4, 5, 7, 10, 13, 14, 17, 20, 21, 24, 27, 28, 31, 34, 35, 38, 41, 42, 45, 48): 'm',
    (0, 2, 3, 4, 6, 7, 11, 12, 17, 18, 23, 24, 29, 30, 35, 36, 41): 'n',
    (1, 2, 3, 4, 6, 11, 12, 17, 18, 23, 24, 29, 30, 35, 37, 38, 39, 40): 'o',
    (0, 2, 3, 4, 6, 7, 11, 12, 17, 18, 23, 24, 29, 30, 31, 35, 36, 38, 39, 40, 42, 48, 54): 'p',
    (1, 2, 3, 5, 6, 10, 11, 12, 17, 18, 23, 24, 29, 30, 34, 35, 37, 38, 39, 41, 47, 53, 59): 'q',
    (0, 2, 3, 4, 6, 7, 11, 12, 18, 24, 30, 36): 'r',
    (1, 2, 3, 4, 6, 11, 12, 19, 20, 21, 22, 29, 30, 35, 37, 38, 39, 40): 's',
    (2, 8, 12, 13, 14, 15, 16, 20, 26, 32, 38, 44, 50, 53, 57, 58): 't',
    (0, 5, 6, 11, 12, 17, 18, 23, 24, 29, 30, 34, 35, 37, 38, 39, 41): 'u',
    (0, 5, 6, 11, 12, 17, 19, 22, 25, 28, 32, 33, 38, 39): 'v',
    (0, 6, 7, 10, 13, 14, 17, 20, 21, 24, 27, 28, 31, 34, 35, 37, 39, 41, 43, 47): 'w',
    (0, 5, 6, 11, 13, 16, 20, 21, 25, 28, 30, 35, 36, 41): 'x',
    (0, 5, 6, 11, 12, 17, 18, 23, 24, 29, 31, 34, 35, 38, 39, 41, 47, 52, 55, 56, 57): 'y',
    (0, 1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 36, 37, 38, 39, 40, 41): 'z',
    (1, 2, 3, 6, 10, 13, 15, 18, 22, 25, 27, 30, 34, 35): '{',
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13): '|',
    (0, 1, 5, 8, 10, 13, 17, 20, 22, 25, 29, 32, 33, 34): '}',
    (1, 2, 6, 7, 10, 13, 14, 18, 19): '~',
}


def get_text(img):
    """
    Extract text from image.
    """
    signatures = get_char_signatures(img)
    chars = [CLASSES[sig] for sig in signatures]
    return ''.join(chars)


def get_value(key):
    """
    Get diagram value.

    ``key`` is the diagram key (``w1`` to ``w6``).

    The diagram is downloaded, its text is extracted, converted to
    float and returned.
    """
    img = get_image(key, 70, 50)
    return float(get_text(img))


@contextlib.contextmanager
def local_locale(name):
    """
    Context-manager to temporarily switch to a different locale.
    """
    old = locale.getlocale(locale.LC_ALL)
    try:
        yield locale.setlocale(locale.LC_ALL, name)
    finally:
        locale.setlocale(locale.LC_ALL, old)


def get_date():
    """
    Get time and date of the last update.

    The date image is downloaded, its text is extracted, converted to
    a ``datetime.datetime`` instance and returned.
    """
    img = get_image('w9', 300, 20)
    label = get_text(img)
    with local_locale('C'):
        date = datetime.datetime.strptime(label.split(':', 1)[1].strip(), '%d %b %y %H:%M')
    return date


def scrape():
    """
    Download and parse data.

    Returns a dictionary with the latest values.
    """
    values = {}
    for key, (name, unit) in VALUES.iteritems():
        values[name] = {
            'unit': unit,
            'value': get_value(key),
        }
    return values


def symlink(target, filename):
    """
    Create a symlink.

    An existing file of the same name is overwritten.
    """
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
    os.symlink(target, filename)


if __name__ == '__main__':
    import codecs
    import errno
    import json
    import logging
    import logging.handlers
    import os
    import os.path
    import sys

    HERE = os.path.abspath(os.path.dirname(__file__))
    log = logging.getLogger('codeforka-trinkwasser')
    log.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] <%(levelname)s> %(message)s')
    file_handler = logging.handlers.TimedRotatingFileHandler(
            os.path.join(HERE, 'scrape.log'), when='W0', backupCount=4,
            encoding='utf8')
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

    log.info('Started')

    if len(sys.argv) != 2:
        log.error('Illegal number of arguments: Expected 1, got %d' %
                  (len(sys.argv) - 1))
        sys.exit(1)
    OUTPUT_DIR = os.path.abspath(sys.argv[1])
    if not os.path.isdir(OUTPUT_DIR):
        log.error('Output directory "%s" does not exist' % OUTPUT_DIR)
        sys.exit(1)
    log.info('Output directory is "%s"' % OUTPUT_DIR)

    try:
        date = get_date().strftime('%Y-%m-%d-%H-%M-00')
        log.info('Date of last measurement: %s', date)
        basename = 'karlsruhe-drinking-water-' + date + '.json'
        filename = os.path.join(OUTPUT_DIR, basename)
        if not os.path.isfile(filename):
            log.info('Scraping data')
            values = scrape()
            with codecs.open(filename, 'w', encoding='utf8') as f:
                json.dump({'date': date, 'values': values}, f,
                          separators=(',',':'))
            symlink(basename, os.path.join(OUTPUT_DIR, 'latest.json'))
        else:
            log.info('Data already scraped, nothing to do')
    except Exception as e:
        log.exception(e)

    log.info('Finished')
