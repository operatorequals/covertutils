from setuptools import setup

import covertutils

import unittest


def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite

setup(name=covertutils.__name__,
      version=covertutils.__version__,
      description='Module for backdoor design and implementation.',
      url=covertutils.__github__,
      author=covertutils.__author__,
      author_email=covertutils.__email__,
      license='MIT',
      packages=[ covertutils.__name__ ],
      zip_safe=False,
	  tests_require=['entropy'],
	  test_suite = 'setup.my_test_suite'
	  )
