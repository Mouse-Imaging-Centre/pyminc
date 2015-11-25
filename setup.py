from setuptools import setup, find_packages

setup(name='pyminc',
      version = '0.41',
      description = "Python interface to libminc",
      url = "https://github.com/Mouse-Imaging-Centre/pyminc",
      author = "Jason Lerch",
      author_email = "jason@mouseimaging.ca",
      license = "BSD",
      packages = find_packages(), #['pyminc', 'pyminc.volumes'],
      install_requires = ["numpy"],
      scripts = ['scripts/sva2mnc.py'],
      test_suite="test",
      )
