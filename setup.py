from distutils.core import setup

setup(name='pyminc',
      version = '0.4',
      author = "Jason Lerch",
      author_email = "jason@mouseimaging.ca",
      packages = ['pyminc', 'pyminc.volumes'],
      scripts = ['scripts/sva2mnc.py'],
      )
