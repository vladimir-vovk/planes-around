# -*- coding: utf-8 -*-
from setuptools import setup

setup(name='planes_around',
      version='1.3.0',
      description='Get info about planes around the specified location using the OpenSky service.',
      url='http://github.com/vladimir-vovk/planes-around',
      author='Vladimir Vovk',
      author_email='vladimir.vovk.at@gmail.com',
      license='MIT',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
          'Natural Language :: English',
          'Topic :: Utilities'
      ],
      keywords='plane location opensky',
      packages=['planes_around'],
      install_requires=['geopy', 'requests', 'folium'],
      python_requires='>=3',
      entry_points={
          'console_scripts': [
              'planes_around=planes_around.cli:main',
          ],
      },
      zip_safe=False)
