from setuptools import setup

setup(name='pyminc',
      version = '0.41',
      author = "Jason Lerch",
      author_email = "jason@mouseimaging.ca",
      packages = ['pyminc', 'pyminc.volumes'],
      scripts = ['scripts/sva2mnc.py'],
      )
