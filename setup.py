import os
from setuptools import setup
import sys


# pip workaround
os.chdir(os.path.abspath(os.path.dirname(__file__)))


with open('README.rst') as fp:
    description = fp.read()
req = ['watchdog',
       'rpaths>=0.7']
if sys.version_info < (2, 7):
    req.append('argparse')
setup(name='gitobox',
      version='0.2',
      packages=['gitobox'],
      package_data={'gitobox': ['hooks/*']},
      entry_points={'console_scripts': [
          'gitobox = gitobox.main:main']},
      install_requires=req,
      description=
          "Synchronizes a directory with a Git repository; particularly "
          "useful to track \"dumb\" collaboration software like DropBox",
      author="Remi Rampin",
      author_email='remirampin@gmail.com',
      maintainer="Remi Rampin",
      maintainer_email='remirampin@gmail.com',
      url='https://github.com/remram44/gitobox',
      long_description=description,
      license='BSD',
      keywords=['git', 'dropbox', 'drive', 'gdrive', 'cloud', 'dumb', 'sync',
                'synchronization', 'collaboration'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Environment :: No Input/Output (Daemon)',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Communications :: File Sharing',
          'Topic :: Internet',
          'Topic :: Software Development :: Version Control'])
