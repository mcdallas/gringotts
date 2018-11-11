from setuptools import setup

setup(
    name='Gringotts',
    author='Mike Dallas',
    author_email='mcdallas@protonmail.com',
    license='MIT',
    keywords="mimblewimble grin cli",
    version='0.1',
    py_modules=['src.cli'],
    install_requires=['Click', 'requests'],
    entry_points='''
        [console_scripts]
        gringotts=src.cli:cli
    '''
)