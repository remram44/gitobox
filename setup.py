import os
from setuptools import setup
import sys


# pip workaround
os.chdir(os.path.abspath(os.path.dirname(__file__)))


with open('README.rst') as fp:
    description = fp.read()
req = ['pyinotify',
       'rpaths']
if sys.version_info < (2, 7):
    req.append('argparse')
setup(name='gitify',
      version='0.1',
      packages=['gitify'],
      entry_points={'console_scripts': [
          'gitify = gitify.main:main']},
      install_requires=req,
      description=
          "Synchronizes a directory with a Git repository; particularly "
          "useful to track \"dumb\" collaboration software like DropBox",
      author="Remi Rampin",
      author_email='remirampin@gmail.com',
      maintainer="Remi Rampin",
      maintainer_email='remirampin@gmail.com',
      url='https://github.com/remram44/gitify',
      long_description=description,
      license='BSD',
      keywords=['git', 'dropbox', 'drive', 'gdrive', 'cloud', 'dumb', 'sync',
                'synchronization', 'collaboration'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: BSD License'])
