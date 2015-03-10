#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import cStringIO
import contextlib
import datetime
import locale as locale_module
import urllib2

import PIL.Image


# Homepage:
# http://www.stadtwerke-karlsruhe.de/swka-de/inhalte/produkte/trinkwasser/online-wert-trinkwasser.php

IMAGE_URL = "http://www.stadtwerke-karlsruhe.de/cgi-bin/gd?h=%d&w=%d&r=255&g=255&b=255&tr=0&tg=0&tb=0&wert=%s&tt=%%20%%20%%20&wnull=0&wmax=25"


VALUES = {
    'w1': ('Temperatur', '°C'),
    'w2': ('PH-Wert', ''),
    'w3': ('Leitfähigkeit', 'µS/cm'),
    'w4': ('Trübung', 'NTU'),
    'w5': ('Sauerstoff', 'mg/l'),
    'w6': ('Nitrat', 'mg/l'),
}

def get_image(key, height, width):
    buf = cStringIO.StringIO(urllib2.urlopen(IMAGE_URL % (height, width, key)).read())
    img = PIL.Image.open(buf)
    return img.crop((1, 1, img.size[0] - 2, img.size[1] - 2))  # Cut 1 pixel border


def count_black_pixels_vertically(img):
    """
    Count an image's black pixel vertically.

    Assumes ``img`` has only one band.
    """
    data = img.getdata()
    columns = img.size[0]
    count = [0] * columns
    for i, d in enumerate(img.getdata()):
        if not d:
            count[i % columns] += 1
    return count


def split(seq):
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


CLASSES = {
    (2, 2): '.',
    (4, 4): ':',
    (6, 2, 2, 2, 2, 6): '0',
    (2, 2, 10, 1, 1): '1',
    (5, 3, 3, 3, 3, 4): '2',
    (4, 2, 3, 3, 3, 7): '3',
    (3, 2, 2, 2, 10, 1): '4',
    (6, 3, 3, 3, 3, 5): '5',
    (7, 3, 3, 3, 3, 4): '6',
    (1, 1, 1, 5, 4, 3): '7',
    (7, 3, 3, 3, 3, 7): '8',
    (3, 3, 3, 3, 3, 7): '9',
    (3, 3, 3, 3, 3, 6): 'a',
    (10, 2, 2, 2, 2, 5): 'b',
    (5, 3, 3, 3, 3, 3): 'e',
    (1, 9, 2, 2, 2, 1): 'f',
    (5, 5, 4, 4, 5, 4): 'g',
    (7, 1, 1, 6, 1, 1, 6): 'm',
    (7, 1, 1, 1, 1, 1): 'r',
    (1, 1, 9, 2, 2, 1): 't',
    (3, 3, 3, 3, 3, 2): 'z',
    (8, 2, 2, 2, 2, 8): 'A',
    (10, 1, 1, 1, 1, 1): 'L',
    (10, 2, 2, 2, 2, 2, 10): 'M',
}

SPACE_WIDTH = 6

def get_text(img):
    blacks = count_black_pixels_vertically(img.convert('L'))
    chars = []
    last_end = float('Inf')
    for start, end in split(blacks):
        if start - last_end >= SPACE_WIDTH:
            chars.append(' ')
        chars.append(CLASSES[tuple(blacks[start : end])])
        last_end = end
    return ''.join(chars)


@contextlib.contextmanager
def locale(name):
    old = locale_module.getlocale(locale_module.LC_ALL)
    try:
        yield locale_module.setlocale(locale_module.LC_ALL, name)
    finally:
        locale_module.setlocale(locale_module.LC_ALL, old)


# Diagrams
for key in sorted(VALUES):
    img = get_image(key, 50, 70)
    name, unit = VALUES[key]
    print "%s: %f %s" % (name, float(get_text(img)), unit)

# Date
img = get_image('w9', 20, 300)
print
label = get_text(img)
with locale('C'):
    date = datetime.datetime.strptime(label.split(':', 1)[1].strip(), '%d %b %y %H:%M')
print 'Datum:', date

