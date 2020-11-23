"""
setup script
"""
from setuptools import setup, find_packages
import spicebox

config = {
    'description': 'Common Code I use in many projects',
    'author': 'Rawser Spicer',
    'url': spicebox.__codeurl__,
    'author_email': spicebox.__email__ ,
    'version': spicebox.__version__,
    'install_requires': [
        'numpy', 
        'gdal', 
        'matplotlib',
    ],
    'packages': find_packages(),
    'scripts': [],
    'package_data': {},
    'name': 'spicebox'
}

setup(**config)
