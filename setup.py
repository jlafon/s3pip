import os
import sys

from setuptools import setup, find_packages

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    print("Now tag me :)")
    print("  git tag -a {0} -m 'version {0}'".format(__import__('s3pip').__version__))
    print("  git push --tags")
    sys.exit()

setup(
    name='s3pip',
    version=__import__('s3pip').__version__,
    packages=find_packages(),
    url='http://jlafon.io',
    author='Jharrod LaFon',
    author_email='jlafon@eyesopen.com',
    description='A pip wrapper that uses AWS S3 for package data',
    long_description=open('README.rst').read(),
    license='MIT',
    zip_safe=False,
    install_requires=[
        'boto',
        'pip>=1.5'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    entry_points={
        'console_scripts': [
            's3pip=s3pip:main',
        ],
    },
)
