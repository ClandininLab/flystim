from setuptools import setup, find_packages

setup(
    name='flystim',
    version='2.0.0',
    description='Visual stimulus generator for fruit fly experiments.',
    long_description='Multi-monitor perspective-corrected visual stimulus generator for fruit fly experiments.',
    url='https://github.com/ClandininLab/flystim',
    author='Steven Herbst',
    author_email='sherbst@stanford.edu',
    packages=['flystim'],
    install_requires=[
        'scipy',
        'numpy',
        'pyglet',
        'moderngl',
        'PyQt5==5.11.2',
        'hidapi',
        'pandas',
        'json-rpc',
        'matplotlib',
        'qimage2ndarray',
        'scikit-image',
    ],
    entry_points={
        'console_scripts': [
            'lcr_ctl=examples.lcr_ctl:main'
        ]
    },
    include_package_data=True,
    zip_safe=False,
)
