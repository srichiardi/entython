from setuptools import setup

setup(name='entython',
      version='0.1',
      description='Graph analysis tool',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Information Analysis',
      ],
      url='https://github.com/srichiardi/entython',
      author='Stefano Richiardi',
      author_email='stefano_richiardi@yahoo.it',
      license='MIT',
      packages=['entython'],
      install_requires=[
          'weakref',
          'datetime',
          'csv',
          'sys',
          're',
      ],
      zip_safe=False)
