try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as file:
    long_description = file.read()

setup(name='poirot',
	  version='0.0.16',
	  description="Investigate a Git repository's revision history to find text patterns.",
	  long_description=long_description,
	  url='https://github.com/dcgov/poirot',
	  license='https://raw.githubusercontent.com/DCgov/poirot/master/LICENSE.md',
	  packages=['poirot'],
	  install_requires=['tqdm>=3.4.0', 'Jinja2>=2.8', 'regex>=2015.11.22'],
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
	  entry_points = {
	  	'console_scripts': [
	  		'little-grey-cells=poirot.commands:littlegreycells',
	  		'big-grey-cells=poirot.commands:biggreycells'
	  		]
	  },
	  zip_safe=False)
