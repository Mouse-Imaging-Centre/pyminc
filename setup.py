from setuptools import setup, find_packages

setup(name='pyminc',
      version = '0.53.3',
      description = "Python interface to libminc",
      url = "https://github.com/Mouse-Imaging-Centre/pyminc",
      author = "Jason Lerch",
      author_email = "jason@mouseimaging.ca",
      license = "BSD",
      packages = find_packages(exclude=["test"]),
      python_requires = ">=3.5",
      install_requires = ["numpy"],
      scripts = ["scripts/sva2mnc.py", "scripts/pyminc_test2.py"],
      tests_require = ["pytest"],
      test_suite="test",
      )
