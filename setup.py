from setuptools import setup

import covertutils


setup(name=covertutils.__name__,
      version=covertutils.__version__,
      description='Module for backdoor design and implementation.',
      url=covertutils.__github__,
      author=covertutils.__author__,
      author_email=covertutils.__email__,
      license='MIT',
      packages=[ covertutils.__name__ ],
      zip_safe=False)
