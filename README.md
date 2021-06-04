Pyminc is a Python interface to the MINC 2 library, allowing use of numpy arrays to 
access MINC data, and other such similar goodies, developed by Jason Lerch.

*****

Documentation can be found in the tutorial section of the MINC Wikibooks (Programming with MINC2 in Python):

http://en.wikibooks.org/wiki/MINC/Tutorials

and some of the basics are described here:

https://github.com/Mouse-Imaging-Centre/pyminc/wiki
*****

Requirements:

Pyminc is compatible with Python 3 only.  It requires Numpy (the Python numerical arrays package) to work;
this can be installed automatically from PyPI via setuptools. Also, it needs MINC2 compiled as a shared object
and accessible through the standard search paths.  For the tests, you also need the `minc-tools` suite
of command-line utilities.

*****

Installing pyminc:

Pyminc is installable from PyPI via setuptools, pip, etc.  To install from source:

1) Untar the tarball if applicable and `cd` into the source directory;
2) Run:
```
python3 setup.py install
```
 with an optional --prefix if you want to install it in a non-default location;
3) Test the installation of the pyminc library run:
```
python3 setup.py test
```
4) At your option, also run the pyminc_test2.py script in the scripts folder. This program has 3 arguments:
   a minc file, a method for smoothing the volume (numpy, blitz or weave) and an output file name.
