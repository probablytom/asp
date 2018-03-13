from setuptools import setup

setup(
    name='Asp',
    version='0.1',
    packages=['asp'],
    package_dir={'': '.'},
    url='https://github.com/probablytom/asp',
    license='',
    author='Tom Wallis, Tim Storer',
    author_email='twallisgm@gmail.com',
    description='Aspect Oriented Programming for Python',
    setup_requires=[],
    test_suite='nose.collector',
    tests_require=['mock', 'nose']
)
