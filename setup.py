from setuptools import setup, find_packages

setup(name='pyminc',
      version = '0.46',
      description = "Python interface to libminc",
      url = "https://github.com/Mouse-Imaging-Centre/pyminc",
      author = "Jason Lerch",
      author_email = "jason@mouseimaging.ca",
      license = "BSD",
      packages = find_packages(),
      install_requires = ["numpy"],
      scripts = ["scripts/sva2mnc.py", "scripts/pyminc_test2.py"],
      test_suite="test",
      )
