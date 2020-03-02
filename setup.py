from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name='flystim',
    version='0.0.1',
    license='MIT',
    description='Visual stimulus generator for fruit fly experiments.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/clandininLab/flystim',
    author='Steven Herbst',
    author_email='sherbst@stanford.edu',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    python_requires='>=3.5',
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
        'flyrpc'
    ],
    entry_points={
        'console_scripts': [
            'lcr_ctl=examples.lcr_ctl:main'
        ]
    },
    include_package_data=True,
    zip_safe=False,
)
