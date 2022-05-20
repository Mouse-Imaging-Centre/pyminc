from setuptools import setup, find_packages

setup(name='pyminc',
      version = '0.57',
      description = "Python interface to libminc",
      url = "https://github.com/Mouse-Imaging-Centre/pyminc",
      author = "Jason Lerch",
      license = "BSD",
      packages = find_packages(exclude=["test"]),
      python_requires = ">=3.7",
      install_requires = ["numpy"],
      scripts = ["scripts/sva2mnc.py", "scripts/pyminc_test2.py"],
      tests_require = ["pytest", "parameterized"],
      test_suite="test",
      )
