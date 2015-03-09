#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import cStringIO
import urllib2

import PIL.Image


# Homepage:
# http://www.stadtwerke-karlsruhe.de/swka-de/inhalte/produkte/trinkwasser/online-wert-trinkwasser.php

IMAGE_URL = "http://www.stadtwerke-karlsruhe.de/cgi-bin/gd?h=50&w=70&r=255&g=255&b=255&tr=0&tg=0&tb=0&wert=%s&tt=%%20%%20%%20&wnull=0&wmax=25"


VALUES = {
    'Temperatur': ('w1', '°C'),
    'PH-Wert': ('w2', None),
    'Leitfähigkeit': ('w3', 'µS/cm'),
    'Trübung': ('w4', 'NTU'),
    'Sauerstoff': ('w5', 'mg/l'),
    'Nitrat': ('w6', 'mg/l'),
}

def get_image(key):
    buf = cStringIO.StringIO(urllib2.urlopen(IMAGE_URL % key).read())
    return PIL.Image.open(buf)


image = get_image('w1')
print image.size

