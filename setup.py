try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='poirot',
	  version='0.0.15',
	  description="Search a git repository's revision history for text patterns.",
	  url='https://github.com/dcgov/poirot',
	  license='https://raw.githubusercontent.com/DCgov/poirot/master/LICENSE.md',
	  packages=['poirot'],
	  install_requires=['tqdm', 'Jinja2', 'regex'],
	  test_suite='nose.collector',
	  tests_require=['nose-progressive'],
	  classifiers=[
	  	'Environment :: Console',
	  	'Intended Audience :: Developers',
	  	'Programming Language :: Python',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5'
	  ],
	  include_package_data=True,
	  scripts=['bin/big-grey-cells', 'bin/little-grey-cells'],
	  zip_safe=False)
