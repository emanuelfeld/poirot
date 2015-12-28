import poirot

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='poirot',
	  version=poirot.__version__,
	  description="Search a git repository's revision history for text patterns.",
	  url='https://github.com/dcgov/poirot',
	  author='Emanuel Feld',
	  license='https://raw.githubusercontent.com/DCgov/poirot/master/LICENSE.md',
	  packages=['poirot'],
	  install_requires=['jinja2', 'tqdm'],
	  test_suite='nose.collector',
	  tests_require=['nose>=1.2.1', 'nose-progressive'],
	  classifiers=[
	  	'Environment :: Console',
	  	'Intended Audience :: Developers',
	  	'Programming Language :: Python'
	  ],
	  include_package_data=True,
	  scripts=['bin/big-grey-cells', 'bin/little-grey-cells'],
	  zip_safe=False)
