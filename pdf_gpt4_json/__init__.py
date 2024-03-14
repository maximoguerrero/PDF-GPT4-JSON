"""
__init__.py

This module is the package initializer for the current Python package.

It's often used to perform setup needed for the package (like import statements). 
In this case, it sets the version of the package and imports all functions from the util module.

__version__ : str
    The version of the package.

util : module
    The utility module containing helper functions used throughout the package.
"""

__version__ = '0.1.1'

from .util import *
