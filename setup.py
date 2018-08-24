from setuptools import setup, find_packages

setup(
    name='flystim',
    version='0.0.1',
    description='Visual stimulus generator for fruit fly experiments.',
    long_description='Multi-monitor perspective-corrected visual stimulus generator for fruit fly experiments.',
    url='https://github.com/sgherbst/flystim',
    author='Steven Herbst',
    author_email='sherbst@stanford.edu',
    packages=['flystim'],
    install_requires=[
        'scipy',
        'numpy',
        'pyglet',
        'moderngl',
	'PyQt5',
	'hidapi',
        'json-rpc'
    ],
    include_package_data=True,
    zip_safe=False,
)
