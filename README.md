Pyminc is a Python interface to the MINC 2 library, allowing use of numpy arrays to 
access MINC data, and other such similar goodies, developed by Jason Lerch.

Documentation can be found in the tutorial section of the MINC Wikibooks (Programming with MINC2 in Python):

http://en.wikibooks.org/wiki/MINC/Tutorials

and some of the basics are described here:

https://github.com/Mouse-Imaging-Centre/pyminc/wiki

# Requirements

For minimum Python version as well as Python dependencies (which will be installed automagically from PyPI during installation), see `setup.py`.
Also, Pyminc needs `libminc` compiled as a shared object and accessible either through the standard search paths or at `MINC_TOOLKIT/lib/libminc2.so` (or `.dylib`).
For the tests, you also need the `minc-tools` suite of command-line utilities.

# Installation:

Pyminc is installable from PyPI:

```
pip3 install pyminc
```

Alternately, to install from source:

1) Clone the repository or download and untar the tarball if applicable and `cd` into the source directory;
2) Run:
```
python3 setup.py install
```
 with an optional --prefix if you want to install it in a non-default location;
3) Test the installation of the pyminc library via:
```
python3 setup.py test
```
4) At your option, also run the pyminc_test2.py script in the scripts folder. This program has 3 arguments:
   a minc file, a method for smoothing the volume (numpy, blitz or weave) and an output file name.
