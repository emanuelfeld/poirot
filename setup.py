from setuptools import setup

setup(name='poirot',
	  version='0.1.0',
	  description="Search a git repository's revision history for text patterns.",
	  url='https://github.com/dcgov/poirot',
	  author='Emanuel Feld',
	  license='https://raw.githubusercontent.com/DCgov/poirot/master/LICENSE.md',
	  packages=['poirot'],
	  install_requires=['jinja2','nose','nose-progressive'],
	  scripts=['bin/big-grey-cells', 'bin/little-grey-cells'],
	  zip_safe=False)
