Quality of Karlsruhe's Drinking Water
=====================================
The [Stadtwerke Karlsruhe][stadtwerke] regularly publish values of
[several quality indicators][indicators] for Karlsruhe's drinking water.
Unfortunately, they only provide the current values and only as images.

This project therefore provides a small scraper that downloads the images,
extracts the numerical values and stores them to disk.

Installation
------------
Most dependencies can be installed via [pip][pip] (ideally into a
[virtualenv][virtualenv]):

    pip install -r requirements.txt

You will also need [the Python bindings][python-gd] for the
[gd graphics library][gd], which are unfortunately not available through
`pip`. On Ubuntu you can install them via

    sudo apt-get install python-gd

License
-------
MIT. See the file `LICENSE` for details.


[stadtwerke]: http://www.stadtwerke-karlsruhe.de
[indicators]: http://www.stadtwerke-karlsruhe.de/swka-de/inhalte/produkte/trinkwasser/online-wert-trinkwasser.php
[pip]: https://pip.pypa.io/en/stable/
[virtualenv]: https://virtualenv.readthedocs.org/en/latest/
[gd]: https://libgd.github.io/
[python-gd]: https://github.com/Solomoriah/gdmodule

