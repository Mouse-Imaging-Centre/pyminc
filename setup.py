from distutils.core import setup

setup(name='pyminc',
      version = '0.2.1',
      author = "Jason Lerch",
      author_email = "jason@phenogenomics.ca",
      packages = ['pyminc', 'pyminc.volumes'],
      scripts = ['scripts/sva2mnc.py'],
      )
